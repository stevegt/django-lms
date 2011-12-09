from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.forms import ModelForm
from django.forms import ModelMultipleChoiceField
from django.contrib.admin.widgets import FilteredSelectMultiple
from permission_backend_nonrel.models import UserPermissionList

from courses.models import Course, Semester, Assignment, AssignmentSubmission, Resource


class CourseAdminForm(ModelForm):
    faculty = ModelMultipleChoiceField(queryset = User.objects.none(),
                                       required = False,
                                       widget = FilteredSelectMultiple("Faculty", False) )
    members = ModelMultipleChoiceField(queryset = User.objects.none(),
                                       required = False,
                                       widget = FilteredSelectMultiple("Faculty", False) )

    def __init__(self,*args,**kwargs):
        super (CourseAdminForm,self ).__init__(*args,**kwargs)

        faculty_group = Group.objects.get_or_create(name = 'Faculty')[0]
        faculty_list = UserPermissionList.objects.filter(group_fk_list = faculty_group.pk)
        self.fields['faculty'].queryset = User.objects.filter(pk__in = [faculty.user.pk for faculty in faculty_list])
        if self.instance:
            self.fields['faculty'].initial = self.instance.faculty

        student_group = Group.objects.get_or_create(name = 'Student')[0]
        student_list = UserPermissionList.objects.filter(group_fk_list = student_group.pk)
        self.fields['members'].queryset = User.objects.filter(pk__in = [student.user.pk for student in student_list])
        if self.instance:
            self.fields['members'].initial = self.instance.members

    class Meta:
        model = Course
        exclude = ('faculty', 'members')

class CourseAdmin(admin.ModelAdmin):
     list_filter = ('semester',)
     #filter_horizontal = ('faculty',)
     form = CourseAdminForm

     def save_model(self, request, obj, form, change):
         super(CourseAdmin, self).save_model(request, obj, form, change)
         try:
             if len(form.cleaned_data["faculty"]) > 0:
                 obj.faculty = list(form.cleaned_data["faculty"])
                 obj.save()
             if len(form.cleaned_data["members"]) > 0:
                 obj.members = list(form.cleaned_data["members"])
                 obj.save()
         except KeyError:
             pass


admin.site.register(Course, CourseAdmin)
admin.site.register(Semester)
#admin.site.register(Assignment)
#admin.site.register(AssignmentSubmission)
#admin.site.register(Resource)
