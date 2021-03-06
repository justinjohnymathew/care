from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.conf import settings

from .forms import (
    FacilityCreationForm,
    FacilityCapacityCreationForm,
    DoctorsCountCreationForm,
)
from .models import Facility, FacilityCapacity, HospitalDoctors


class StaffRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type == settings.STAFF_ACCOUNT_TYPE:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect_to_login(self.request.get_full_path())


class FacilitiesView(LoginRequiredMixin, StaffRequiredMixin, View):

    template = "facility/facilities_view.html"

    def get(self, request):
        try:
            current_user = request.user
            data = Facility.objects.filter(created_by=current_user)
            return render(request, self.template, {"data": data})
        except Exception as e:
            print(e)
            return HttpResponseRedirect("")


class FacilityView(LoginRequiredMixin, StaffRequiredMixin, View):

    template = "facility/facility_view.html"

    def get(self, request, pk):
        try:
            current_user = request.user
            facility_obj = Facility.objects.get(id=pk, created_by=current_user)
            capacities = FacilityCapacity.objects.filter(facility=facility_obj)
            doctor_counts = HospitalDoctors.objects.filter(facility=facility_obj)
            return render(
                request,
                self.template,
                {
                    "capacities": capacities,
                    "doctor_counts": doctor_counts,
                    "facility": facility_obj,
                },
            )
        except Exception as e:
            print(e)
            return HttpResponseRedirect("")


class FacilityCreation(LoginRequiredMixin, StaffRequiredMixin, View):

    form_class = FacilityCreationForm
    template = "facility/facility_creation.html"

    def get(self, request):
        try:
            form = self.form_class()
            return render(request, self.template, {"form": form})
        except Exception as e:
            print(e)
            return HttpResponseRedirect("")

    def post(self, request):
        try:
            data = request.POST
            form = self.form_class(data)
            if form.is_valid():
                facility_obj = form.save(commit=False)
                facility_obj.created_by = request.user
                facility_obj.facility_type = 2
                facility_obj.save()
                return HttpResponseRedirect(
                    "/facility/{}/capacity/add".format(facility_obj.id)
                )
            return render(request, self.template, {"form": form})
        except Exception as e:
            print(e)
            return HttpResponseRedirect("")


class FacilityCapacityCreation(LoginRequiredMixin, StaffRequiredMixin, View):
    form_class = FacilityCapacityCreationForm
    template = "facility/facility_capacity_creation.html"

    def get(self, request, pk):
        try:
            form = self.form_class()
            current_user = request.user
            facility_obj = Facility.objects.get(id=pk, created_by=current_user)
            return render(
                request, self.template, {"form": form, "facility": facility_obj}
            )
        except Exception as e:
            print(e)
            return HttpResponseRedirect("")

    def post(self, request, pk):
        try:
            data = request.POST
            form = self.form_class(data)
            if form.is_valid():
                duplicate = False
                facility_capacity_obj = form.save(commit=False)
                facility_obj = Facility.objects.get(id=pk)
                facility_capacity_obj.facility = facility_obj
                try:
                    facility_capacity_obj.save()
                    if "addmore" in data:
                        return redirect(
                            "facility:facility-capacity-create", facility_obj.id
                        )
                    else:
                        return redirect(
                            "facility:facility-doctor-count-create", facility_obj.id
                        )
                except IntegrityError:
                    duplicate = True
            return render(
                request, self.template, {"form": form, "duplicate": duplicate}
            )
        except Exception as e:
            print(e)
            return HttpResponseRedirect("")


class FacilityCapacityUpdation(LoginRequiredMixin, StaffRequiredMixin, View):
    form_class = FacilityCapacityCreationForm
    template = "facility/facility_capacity_updation.html"

    def get(self, request, fpk, cpk):
        try:
            current_user = request.user
            facility_obj = Facility.objects.get(id=fpk, created_by=current_user)
            capacity_obj = FacilityCapacity.objects.get(id=cpk, facility=facility_obj)
            form = self.form_class(instance=capacity_obj)
            return render(
                request, self.template, {"form": form, "facility": facility_obj}
            )
        except Exception as e:
            print(e)
            return HttpResponseRedirect("")

    def post(self, request, fpk, cpk):
        try:
            data = request.POST
            current_user = request.user
            facility_obj = Facility.objects.get(id=fpk, created_by=current_user)
            capacity_obj = FacilityCapacity.objects.get(id=cpk, facility=facility_obj)
            form = self.form_class(data, instance=capacity_obj)
            duplicate = False
            if form.is_valid():
                try:
                    form.save()
                    return redirect("facility:facility-view", facility_obj.id)
                except IntegrityError:
                    duplicate = True
            return render(
                request, self.template, {"form": form, "duplicate": duplicate}
            )
        except Exception as e:
            print(e)
            return HttpResponseRedirect("")


class DoctorCountCreation(LoginRequiredMixin, StaffRequiredMixin, View):
    form_class = DoctorsCountCreationForm
    template = "facility/facility_doctor_count_creation.html"

    def get(self, request, pk):
        try:
            form = self.form_class()
            current_user = request.user
            facility_obj = Facility.objects.get(id=pk, created_by=current_user)
            return render(
                request, self.template, {"form": form, "facility": facility_obj}
            )
        except Exception as e:
            return HttpResponseRedirect("")

    def post(self, request, pk):
        try:
            data = request.POST
            form = self.form_class(data)
            if form.is_valid():
                duplicate = False
                facility_capacity_obj = form.save(commit=False)
                facility_obj = Facility.objects.get(id=pk)
                facility_capacity_obj.facility = facility_obj
                try:
                    facility_capacity_obj.save()
                    if "addmore" in data:
                        return redirect(
                            "facility:facility-doctor-count-create", facility_obj.id
                        )
                    else:
                        return redirect("facility:facility-view", facility_obj.id)
                except IntegrityError:
                    duplicate = True
            return render(
                request, self.template, {"form": form, "duplicate": duplicate}
            )
        except Exception as e:
            return HttpResponseRedirect("")


class DoctorCountUpdation(LoginRequiredMixin, StaffRequiredMixin, View):
    form_class = DoctorsCountCreationForm
    template = "facility/facility_doctor_count_updation.html"

    def get(self, request, fpk, cpk):
        try:
            current_user = request.user
            facility_obj = Facility.objects.get(id=fpk, created_by=current_user)
            doctor_count_obj = HospitalDoctors.objects.get(
                id=cpk, facility=facility_obj
            )
            form = self.form_class(instance=doctor_count_obj)
            return render(
                request, self.template, {"form": form, "facility": facility_obj}
            )
        except Exception as e:
            print(e)
            return HttpResponseRedirect("")

    def post(self, request, fpk, cpk):
        try:
            data = request.POST
            current_user = request.user
            facility_obj = Facility.objects.get(id=fpk, created_by=current_user)
            doctor_count_obj = HospitalDoctors.objects.get(
                id=cpk, facility=facility_obj
            )
            form = self.form_class(data, instance=doctor_count_obj)
            duplicate = False
            if form.is_valid():
                try:
                    form.save()
                    return redirect("facility:facility-view", facility_obj.id)
                except IntegrityError:
                    duplicate = True
            return render(
                request, self.template, {"form": form, "duplicate": duplicate}
            )
        except Exception as e:
            print(e)
            return HttpResponseRedirect("")
