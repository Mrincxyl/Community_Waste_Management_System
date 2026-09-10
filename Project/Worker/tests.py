from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from UserAuth.models import Municipality, WorkerProfile, customUser


class WorkerManagementTests(TestCase):
    def setUp(self):
        self.municipality_user = customUser.objects.create_user(
            username="municipality_officer",
            email="municipality@example.com",
            phone="9876543210",
            full_name="Municipality Officer",
            role="municipality",
            password="StrongPass123!",
        )

        self.municipality = Municipality.objects.create(
            user=self.municipality_user,
            organization_name="Green City Municipality",
            designation="Environmental Officer",
            official_email="official@greencity.gov",
            phone="9876543211",
            address="Main Office Road",
            state="Test State",
            district="Test District",
            city="Test City",
            verification_document=SimpleUploadedFile(
                "doc.pdf",
                b"municipality document",
                content_type="application/pdf",
            ),
            status="approved",
        )

        self.worker_user = customUser.objects.create_user(
            username="worker_alpha",
            email="worker@example.com",
            phone="9876543212",
            full_name="Worker Alpha",
            role="worker",
            password="StrongPass123!",
        )

        self.worker = WorkerProfile.objects.create(
            user=self.worker_user,
            municipality=self.municipality,
            employee_id="EMP0001",
            ward="Ward 5",
            status="available",
        )

        self.client.force_login(self.municipality_user)

    def test_delete_worker_removes_worker_and_user(self):
        response = self.client.get(reverse("delete_worker", args=[self.worker.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(WorkerProfile.objects.filter(pk=self.worker.pk).exists())
        self.assertFalse(customUser.objects.filter(pk=self.worker_user.pk).exists())
