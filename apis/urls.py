from django.urls import path
from .views import *


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('departments/', DepartmentListCreateView.as_view(), name='department-list-create'),
    path('patient_records/', PatientRecordView.as_view(), name='patient-record-list'),
    path('patients/<int:pk>/', PatientDetailView.as_view(), name='patient-detail'),
    path('doctors/<int:pk>/', DoctorProfileView.as_view(), name='doctor-profile-detail'),
    path('patient_records/<int:pk>/', PatientRecordDetailView.as_view(), name='patient-record-detail'),
    path('doctors/', DoctorListView.as_view(), name='doctor-list'),
    path('patients/', PatientListView.as_view(), name='patient-list'),
    path('department/<int:pk>/doctors/', DepartmentDoctorListView.as_view(), name='department-doctors'),
    path('department/<int:pk>/patients/', DepartmentPatientListView.as_view(), name='department-patients'),
]
