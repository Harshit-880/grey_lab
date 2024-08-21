from rest_framework import serializers
from .models import User, Department, DoctorProfile, PatientProfile, PatientRecords



class UserRegistrationSerializer(serializers.ModelSerializer):
  # We are writing this becoz we need confirm password field in our Registratin Request
  password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)
  class Meta:
    model = User
    fields=['email', 'name', 'password', 'password2', 'role']
    extra_kwargs={
      'password':{'write_only':True}
    }

  # Validating Password and Confirm Password while Registration
  def validate(self, attrs):
    password = attrs.get('password')
    password2 = attrs.get('password2')
    if password != password2:
      raise serializers.ValidationError("Password and Confirm Password doesn't match")
    return attrs

  def create(self, validate_data):
    
    return User.objects.create_user(**validate_data)
  

class UserLoginSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(max_length=255)
  class Meta:
    model = User
    fields = ['email', 'password']


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh = attrs.get('refresh')
        if not refresh:
            raise serializers.ValidationError("Refresh token is required.")
        return attrs
    

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email,', 'name', 'role']

# Department Serializer
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'diagnostics', 'location', 'specialization']



class PatientRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientRecords
        fields = '__all__'
        read_only_fields = ['doctor', 'department']  # These fields are auto-filled

    def validate(self, data):
        doctor = self.context['request'].user
        patient = data['patient']

        # Ensure the doctor and patient are in the same department
        if doctor.doctorprofile.department != patient.department:
            raise serializers.ValidationError("Doctor and patient must be in the same department.")
        
        # Automatically assign the department
        data['department'] = doctor.doctorprofile.department
        return data

    def create(self, validated_data):
        doctor = self.context['request'].user.doctorprofile
        validated_data['doctor'] = doctor
        return super().create(validated_data)
    

class PatientProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = PatientProfile
        fields = ['id', 'user_name', 'department_name', 'department', 'user']  # Replace '...' with actual fields
        read_only_fields = ['user', 'department']  # 'department' will be automatically filled on update

    def update(self, instance, validated_data):
        doctor = self.context['request'].user
        department = doctor.doctorprofile.department

        # Update the department to match the doctor's department
        instance.department = department
        instance.save()
        return instance
    
class DoctorProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()

    class Meta:
        model = DoctorProfile
        fields = ['id', 'username', 'department_name']
        read_only_fields = ['username', 'department_name']  # These fields are read-only

    def get_username(self, obj):
        return obj.user.name  # Assuming the `name` field is used for username

    def get_department_name(self, obj):
        return obj.department.name if obj.department else "No Department"
    


class PatientRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientRecords
        fields = '__all__'
        read_only_fields = ['doctor', 'department']  # doctor and department are automatically filled

    def validate(self, data):
        doctor = self.context['request'].user

        # Ensure the doctor is in the same department as the patient
        if 'patient' in data:
            patient_profile = data['patient']
            if patient_profile.department != doctor.doctorprofile.department:
                raise serializers.ValidationError("Doctor and patient must be in the same department.")

        return data
    
class DoctorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = ['id', 'user']
        read_only_fields = ['id', 'user']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['name'] = instance.user.name  # Assuming `name` field in User model
        return representation
    
class PatientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = ['id', 'user']
        read_only_fields = ['id', 'user']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['name'] = instance.user.name  # Assuming `name` field in User model
        return representation


class DoctorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = ['id', 'user', 'department']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['name'] = instance.user.name  # Assuming `name` field in User model
        representation['department'] = instance.department.name  # Assuming `name` field in Department model
        return representation
    

class PatientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = ['id', 'user', 'department']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['name'] = instance.user.name  # Assuming `username` field in User model
        representation['department'] = instance.department.name  # Assuming `name` field in Department model
        return representation