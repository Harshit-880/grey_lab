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
    print(f"Attempting to authenticate: email={email}, password={password}")
    print(f"User exists: {User.objects.filter(email=email).exists()}")

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

# List Doctors in a Department (Function-Based)
class DepartmentDoctorsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        department = get_object_or_404(Department, pk=pk)
        doctors = DoctorProfile.objects.filter(department=department)
        serializer = DoctorProfileSerializer(doctors, many=True)
        return Response(serializer.data)

# List Patients in a Department (Function-Based)
class DepartmentPatientsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        department = get_object_or_404(Department, pk=pk)
        patients = PatientProfile.objects.filter(department=department)
        serializer = PatientProfileSerializer(patients, many=True)
        return Response(serializer.data)
    
class PatientRecordsListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientRecordsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PatientRecords.objects.filter(doctor__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(doctor=self.request.user.doctorprofile)

# Retrieve, Update, and Delete a Patient Record (Class-Based)
class PatientRecordsDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientRecordsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        if user.role == 'Patient':
            return get_object_or_404(PatientRecords, patient=user.patientprofile, pk=self.kwargs['pk'])
        return get_object_or_404(PatientRecords, doctor__user=user, pk=self.kwargs['pk'])
    

class PatientListCreateView(generics.ListCreateAPIView):
    queryset = PatientProfile.objects.all()
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated]

# Retrieve, Update, and Delete a Patient Profile (Class-Based)
class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PatientProfile.objects.all()
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        if user.role == 'Patient':
            return user.patientprofile
        return get_object_or_404(PatientProfile, pk=self.kwargs['pk'], department=user.doctorprofile.department)
    

class DoctorListCreateView(generics.ListCreateAPIView):
    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated]

# Retrieve, Update, and Delete a Doctor Profile (Class-Based)
class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.doctorprofile
    





class DoctorProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        doctor = get_object_or_404(DoctorProfile, user=request.user)
        serializer = ProfileUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            department = serializer.validated_data.get('department')
            
            if department:
                doctor.department = department
                doctor.save()
            
            return Response({'message': 'Doctor profile updated successfully'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)