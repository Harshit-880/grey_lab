from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from apis.serializers import  *
from django.contrib.auth import authenticate
from apis.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import *
from django.shortcuts import get_object_or_404
from rest_framework import generics
from django.shortcuts import redirect


# Create your views here.

def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)
  return {
      'refresh': str(refresh),
      'access': str(refresh.access_token),
  }


class UserRegistrationView(APIView):
  renderer_classes = [UserRenderer]

  def post(self, request, format=None):
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token = get_tokens_for_user(user)
    return Response({'token':token, 'msg':'Registration Successful'}, status=status.HTTP_201_CREATED)

class UserLoginView(APIView):
  renderer_classes = [UserRenderer]

  def post(self, request, format=None):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get('email')
    password = serializer.data.get('password')

    user = authenticate(email=email, password=password)

    if user is not None:
      token = get_tokens_for_user(user)
      return Response({'token':token, 'msg':'Login Success'}, status=status.HTTP_200_OK)
    else:
      return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data['refresh']
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"msg": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



# List and Create Departments (Function-Based)
class DepartmentListCreateView(APIView):
    def get(self, request):
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)



class PatientRecordView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]  # Use the custom renderer

    def get(self, request, *args, **kwargs):
        doctor = request.user
        department = doctor.doctorprofile.department

        # Fetch all records where the patient is in the same department as the doctor
        records = PatientRecords.objects.filter(department=department)
        
        if not records.exists():
            return Response({"message": "No records exist for your department."}, status=status.HTTP_200_OK)
        
        serializer = PatientRecordSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        doctor = request.user
        serializer = PatientRecordSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save(doctor=doctor.doctorprofile)  # Ensure the doctor is a DoctorProfile instance
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatientDetailView(APIView):
    renderer_classes = [UserRenderer]  # Use the custom renderer

    def get(self, request, pk, *args, **kwargs):
        doctor = request.user
        patient = get_object_or_404(PatientProfile, pk=pk)

        # Allow fetching if the department is the same or NULL
        if patient.department is None or patient.department == doctor.doctorprofile.department:
            serializer = PatientProfileSerializer(patient)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "You do not have permission to view this patient profile."}, status=status.HTTP_403_FORBIDDEN)

    def put(self, request, pk, *args, **kwargs):
        doctor = request.user
        patient = get_object_or_404(PatientProfile, pk=pk)

        # Allow updating only if the doctor and patient are in the same department
        if patient.department is None or patient.department == doctor.doctorprofile.department:
            serializer = PatientProfileSerializer(patient, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "You do not have permission to update this patient profile."}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk, *args, **kwargs):
        doctor = request.user
        patient = get_object_or_404(PatientProfile, pk=pk)

        # Allow deletion if the department is the same or NULL
        if patient.department is None or patient.department == doctor.doctorprofile.department:
            user = patient.user
            patient.delete()
            user.delete()
            return Response({"success": "Patient profile and associated user deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "You do not have permission to delete this patient profile."}, status=status.HTTP_403_FORBIDDEN)


class DoctorProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        try:
            doctor_profile = DoctorProfile.objects.get(pk=pk, user=request.user)
        except DoctorProfile.DoesNotExist:
            return Response({"message": "Profile does not exist."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DoctorProfileSerializer(doctor_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        try:
            doctor_profile = DoctorProfile.objects.get(pk=pk, user=request.user)
        except DoctorProfile.DoesNotExist:
            return Response({"message": "Profile does not exist."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DoctorProfileSerializer(doctor_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        try:
            doctor_profile = DoctorProfile.objects.get(pk=pk, user=request.user)
        except DoctorProfile.DoesNotExist:
            return Response({"message": "Profile does not exist."}, status=status.HTTP_404_NOT_FOUND)

        doctor_profile.delete()
        return Response({"message": "Profile deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    


class PatientRecordDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        try:
            record = PatientRecords.objects.get(pk=pk)
        except PatientRecords.DoesNotExist:
            return Response({"message": "Record does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the requesting doctor is in the same department as the patient record
        doctor = request.user
        if record.department != doctor.doctorprofile.department:
            return Response({"message": "You do not have permission to access this record."}, status=status.HTTP_403_FORBIDDEN)

        serializer = PatientRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        try:
            record = PatientRecords.objects.get(pk=pk)
        except PatientRecords.DoesNotExist:
            return Response({"message": "Record does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the requesting doctor is in the same department as the patient record
        doctor = request.user
        if record.department != doctor.doctorprofile.department:
            return Response({"message": "You do not have permission to update this record."}, status=status.HTTP_403_FORBIDDEN)

        serializer = PatientRecordSerializer(record, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        try:
            record = PatientRecords.objects.get(pk=pk)
        except PatientRecords.DoesNotExist:
            return Response({"message": "Record does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the requesting doctor is in the same department as the patient record
        doctor = request.user
        if record.department != doctor.doctorprofile.department:
            return Response({"message": "You do not have permission to delete this record."}, status=status.HTTP_403_FORBIDDEN)

        record.delete()
        return Response({"message": "Record deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
class DoctorListView(APIView):
    def get(self, request, *args, **kwargs):
        doctors = DoctorProfile.objects.all()
        serializer = DoctorListSerializer(doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        # Redirect to the login URL (replace with your actual login URL)
        return redirect('register')

class PatientListView(APIView):
    def get(self, request, *args, **kwargs):

        patients = PatientProfile.objects.all()
        serializer = PatientListSerializer(patients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        # Redirect to the registration URL (replace with your actual registration URL)
        return redirect('register')


class DepartmentDoctorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        try:
            department = Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            return Response({"error": "Department not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the requesting doctor is from the same department
        doctor = request.user.doctorprofile
        if doctor.department != department:
            return Response({"error": "You do not have permission to view doctors in this department."}, status=status.HTTP_403_FORBIDDEN)

        doctors = DoctorProfile.objects.filter(department=department)
        serializer = DoctorListSerializer(doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class DepartmentPatientListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        try:
            department = Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            return Response({"error": "Department not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the requesting doctor is from the same department
        doctor = request.user.doctorprofile
        if doctor.department != department:
            return Response({"error": "You do not have permission to view patients in this department."}, status=status.HTTP_403_FORBIDDEN)

        patients = PatientProfile.objects.filter(department=department)
        serializer = PatientListSerializer(patients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)