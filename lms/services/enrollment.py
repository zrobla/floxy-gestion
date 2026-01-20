from lms.models import Enrollment


def enroll_user(user, course) -> Enrollment:
    enrollment, _ = Enrollment.objects.get_or_create(user=user, course=course)
    return enrollment
