import io
from unittest.mock import patch

from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from UserAuth.models import Municipality, customUser
from WasteReport.models import Notification, WasteReport


class WasteReportCreationTests(TestCase):
    def setUp(self):
        self.user = customUser.objects.create_user(
            username="citizen1",
            email="citizen1@example.com",
            phone="9876543210",
            full_name="Citizen One",
            password="StrongPass123!",
            role="public",
        )

        self.municipality_user = customUser.objects.create_user(
            username="municipality1",
            email="municipality1@example.com",
            phone="9876543211",
            full_name="Municipality One",
            password="StrongPass123!",
            role="municipality",
        )

        self.municipality = Municipality.objects.create(
            user=self.municipality_user,
            organization_name="Green City",
            designation="Sanitation Officer",
            official_email="official@example.com",
            phone="9876543212",
            address="Main Street",
            state="West Bengal",
            district="Kolkata",
            city="Kolkata",
            verification_document=SimpleUploadedFile("doc.pdf", b"pdf-content", content_type="application/pdf"),
            status="approved",
        )

    def _create_valid_image(self):
        image = Image.new("RGB", (10, 10), color="green")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return SimpleUploadedFile("waste.png", buffer.getvalue(), content_type="image/png")

    @patch("WasteReport.views.wd.predict_waste", return_value={"detect_res": 1})
    def test_report_creation_saves_report_before_notification(self, mock_predict):
        self.client.login(username="citizen1", password="StrongPass123!")

        response = self.client.post(
            reverse("report_waste"),
            {
                "title": "Garbage dump near school",
                "waste_type": "household",
                "description": "Large pile of waste near the school gate.",
                "image": self._create_valid_image(),
                "urgency_level": "high",
                "landmark": "Near school gate",
                "latitude": "22.5726",
                "longitude": "88.3639",
                "state": "West Bengal",
                "district": "Kolkata",
                "city": "Kolkata",
                "full_address": "School Road, Kolkata, West Bengal",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(WasteReport.objects.filter(title="Garbage dump near school").exists())
        self.assertTrue(Notification.objects.filter(user=self.municipality_user).exists())
        mock_predict.assert_called_once()
