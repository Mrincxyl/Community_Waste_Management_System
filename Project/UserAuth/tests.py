from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from WasteReport.models import WasteReport, Notification
from .forms import MunicipalityForm
from .models import Municipality, WorkerProfile, customUser as User


class RegisterViewTests(TestCase):
    def test_municipality_form_restricts_state_and_district_choices(self):
        form = MunicipalityForm()

        self.assertEqual(form.fields["state"].choices, [("West Bengal", "West Bengal")])
        self.assertIn(("Bankura", "Bankura"), form.fields["district"].choices)
        self.assertIn(("Kolkata", "Kolkata"), form.fields["district"].choices)
        self.assertNotIn(("Delhi", "Delhi"), form.fields["district"].choices)

    def test_municipality_worker_management_pages_use_officer_template(self):
        municipality_user = User.objects.create_user(
            username="municipality_user_template",
            email="municipality_template@example.com",
            password="secret123",
            full_name="Municipality Template User",
            phone="9000000099",
            role="municipality",
        )
        Municipality.objects.create(
            user=municipality_user,
            organization_name="Green City",
            designation="Environmental Officer",
            official_email="official_template@example.com",
            phone="9000000099",
            address="Main Road",
            state="West Bengal",
            district="Kolkata",
            city="Kolkata",
            verification_document=SimpleUploadedFile("doc.pdf", b"doc"),
            status="approved",
        )

        self.client.force_login(municipality_user)
        worker_list_response = self.client.get(reverse("worker_list"))
        self.assertEqual(worker_list_response.status_code, 200)
        self.assertTemplateUsed(worker_list_response, "municipality/base_municipality.html")

    def test_public_signup_without_role_selection_creates_public_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "full_name": "Jane Public",
                "email": "jane@example.com",
                "phone": "1234567890",
                "password": "secret123",
                "confirm_password": "secret123",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="jane@example.com").exists())
        self.assertEqual(User.objects.get(email="jane@example.com").role, "public")

    def test_municipality_assigns_worker_and_public_report_shows_assignment_tag(self):
        municipality_user = User.objects.create_user(
            username="municipality_user",
            email="municipality@example.com",
            password="secret123",
            full_name="Municipality Officer",
            phone="9000000000",
            role="municipality",
        )
        municipality = Municipality.objects.create(
            user=municipality_user,
            organization_name="Green City",
            designation="Environmental Officer",
            official_email="official@example.com",
            phone="9000000000",
            address="Main Road",
            state="State A",
            district="District A",
            city="City A",
            verification_document=SimpleUploadedFile("doc.pdf", b"doc"),
            status="approved",
        )

        worker_user = User.objects.create_user(
            username="worker_user",
            email="worker@example.com",
            password="secret123",
            full_name="Field Worker",
            phone="9000000001",
            role="worker",
        )
        worker = WorkerProfile.objects.create(
            user=worker_user,
            municipality=municipality,
            employee_id="W-1001",
            ward="Ward 1",
            status="available",
            is_active=True,
        )

        public_user = User.objects.create_user(
            username="public_user",
            email="public@example.com",
            password="secret123",
            full_name="Public User",
            phone="9000000002",
            role="public",
        )
        report = WasteReport.objects.create(
            user=public_user,
            title="Illegal dump spot",
            waste_type="household",
            description="Need cleanup here.",
            urgency_level="high",
            landmark="City Center",
            state="State A",
            district="District A",
            city="City A",
            assigned_municipality=municipality,
            status="pending",
        )

        self.client.force_login(municipality_user)
        response = self.client.post(
            reverse("municipality_assign_worker", args=[report.id]),
            {"worker": worker.id},
        )

        self.assertEqual(response.status_code, 302)
        report.refresh_from_db()
        self.assertEqual(report.assigned_worker_id, worker.id)
        self.assertEqual(report.status, "in_progress")
        self.assertEqual(WorkerProfile.objects.get(pk=worker.id).status, "busy")

        self.client.force_login(public_user)
        public_response = self.client.get(reverse("my_reports"))
        self.assertContains(public_response, "Assigned to Worker")

    def test_municipality_assign_worker_page_loads(self):
        municipality_user = User.objects.create_user(
            username="municipality_user_2",
            email="municipality2@example.com",
            password="secret123",
            full_name="Municipality Officer Two",
            phone="9000000003",
            role="municipality",
        )
        municipality = Municipality.objects.create(
            user=municipality_user,
            organization_name="Green City 2",
            designation="Officer",
            official_email="official2@example.com",
            phone="9000000003",
            address="Main Road 2",
            state="State B",
            district="District B",
            city="City B",
            verification_document=SimpleUploadedFile("doc2.pdf", b"doc"),
            status="approved",
        )

        public_user = User.objects.create_user(
            username="public_user_2",
            email="public2@example.com",
            password="secret123",
            full_name="Public User Two",
            phone="9000000004",
            role="public",
        )
        report = WasteReport.objects.create(
            user=public_user,
            title="Another dump issue",
            waste_type="organic",
            description="Needs cleanup.",
            urgency_level="medium",
            landmark="Square",
            state="State B",
            district="District B",
            city="City B",
            assigned_municipality=municipality,
            status="pending",
        )

        WorkerProfile.objects.create(
            user=User.objects.create_user(
                username="worker_user_2",
                email="worker2@example.com",
                password="secret123",
                full_name="Field Worker Two",
                phone="9000000005",
                role="worker",
            ),
            municipality=municipality,
            employee_id="W-2001",
            ward="Ward 2",
            status="available",
            is_active=True,
        )

        self.client.force_login(municipality_user)
        response = self.client.get(reverse("municipality_assign_worker", args=[report.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "worker/assign_worker.html")

    def test_assignment_creates_worker_notification_and_worker_notification_opens_worker_dashboard(self):
        municipality_user = User.objects.create_user(
            username="municipality_user_notification",
            email="municipality_notification@example.com",
            password="secret123",
            full_name="Municipality Notification Officer",
            phone="9000000010",
            role="municipality",
        )
        municipality = Municipality.objects.create(
            user=municipality_user,
            organization_name="Green City Notification",
            designation="Officer",
            official_email="official_notification@example.com",
            phone="9000000010",
            address="Main Road",
            state="West Bengal",
            district="Kolkata",
            city="Kolkata",
            verification_document=SimpleUploadedFile("doc.pdf", b"doc"),
            status="approved",
        )

        worker_user = User.objects.create_user(
            username="worker_notification_user",
            email="worker_notification@example.com",
            password="secret123",
            full_name="Assigned Worker",
            phone="9000000011",
            role="worker",
        )
        worker = WorkerProfile.objects.create(
            user=worker_user,
            municipality=municipality,
            employee_id="W-4001",
            ward="Ward 4",
            status="available",
            is_active=True,
        )

        public_user = User.objects.create_user(
            username="public_notification_user",
            email="public_notification@example.com",
            password="secret123",
            full_name="Public Reporter",
            phone="9000000012",
            role="public",
        )
        report = WasteReport.objects.create(
            user=public_user,
            title="Notification test dump",
            waste_type="household",
            description="Notification required",
            urgency_level="high",
            landmark="Main Junction",
            state="West Bengal",
            district="Kolkata",
            city="Kolkata",
            assigned_municipality=municipality,
            status="pending",
        )

        self.client.force_login(municipality_user)
        self.client.post(
            reverse("municipality_assign_worker", args=[report.id]),
            {"worker": worker.id},
        )

        self.assertTrue(
            Notification.objects.filter(user=worker_user, report=report).exists()
        )

        self.client.force_login(worker_user)
        notification = Notification.objects.get(user=worker_user, report=report)
        response = self.client.get(reverse("open_notification", args=[notification.id]))

        self.assertRedirects(response, reverse("worker_dashboard"))

    def test_worker_can_upload_proof_image_before_marking_report_resolved(self):
        municipality_user = User.objects.create_user(
            username="municipality_user_3",
            email="municipality3@example.com",
            password="secret123",
            full_name="Municipality Officer Three",
            phone="9000000006",
            role="municipality",
        )
        municipality = Municipality.objects.create(
            user=municipality_user,
            organization_name="Green City 3",
            designation="Officer",
            official_email="official3@example.com",
            phone="9000000006",
            address="Main Road 3",
            state="State C",
            district="District C",
            city="City C",
            verification_document=SimpleUploadedFile("doc3.pdf", b"doc"),
            status="approved",
        )

        worker_user = User.objects.create_user(
            username="worker_user_3",
            email="worker3@example.com",
            password="secret123",
            full_name="Field Worker Three",
            phone="9000000007",
            role="worker",
        )
        worker = WorkerProfile.objects.create(
            user=worker_user,
            municipality=municipality,
            employee_id="W-3001",
            ward="Ward 3",
            status="available",
            is_active=True,
        )

        public_user = User.objects.create_user(
            username="public_user_3",
            email="public3@example.com",
            password="secret123",
            full_name="Public User Three",
            phone="9000000008",
            role="public",
        )
        report = WasteReport.objects.create(
            user=public_user,
            title="Blocked drain",
            waste_type="construction",
            description="Drain needs cleaning.",
            urgency_level="high",
            landmark="Main Square",
            state="State C",
            district="District C",
            city="City C",
            assigned_municipality=municipality,
            status="in_progress",
            assigned_worker=worker,
        )

        self.client.force_login(worker_user)
        proof = SimpleUploadedFile("proof.jpg", b"proof-bytes", content_type="image/jpeg")
        response = self.client.post(
            reverse("complete_assigned_report", args=[report.id]),
            {
                "action": "resolved",
                "proof_image": proof,
                "latitude": "12.9716",
                "longitude": "77.5946",
            },
        )

        self.assertEqual(response.status_code, 302)
        report.refresh_from_db()
        self.assertEqual(report.status, "resolved")
        self.assertTrue(report.proof_image)
        self.assertEqual(str(report.latitude), "12.971600")
        self.assertEqual(str(report.longitude), "77.594600")
        self.assertEqual(report.assigned_worker_id, worker.id)

        dashboard_response = self.client.get(reverse("worker_dashboard"))
        self.assertContains(dashboard_response, "Completed")
        self.assertContains(dashboard_response, "1")

    def test_worker_and_officer_login_pages_link_to_forgot_password(self):
        officer_response = self.client.get(reverse("officer_login"))
        self.assertEqual(officer_response.status_code, 200)
        self.assertContains(officer_response, reverse("forget_password"))

        worker_response = self.client.get(reverse("worker_login"))
        self.assertEqual(worker_response.status_code, 200)
        self.assertContains(worker_response, reverse("forget_password"))

    def test_worker_must_upload_proof_image_and_geo_location_when_completing_report(self):
        municipality_user = User.objects.create_user(
            username="municipality_user_geo",
            email="municipality_geo@example.com",
            password="secret123",
            full_name="Municipality Geo Officer",
            phone="9000000018",
            role="municipality",
        )
        municipality = Municipality.objects.create(
            user=municipality_user,
            organization_name="Green City Geo",
            designation="Officer",
            official_email="official_geo@example.com",
            phone="9000000018",
            address="Main Road Geo",
            state="West Bengal",
            district="Kolkata",
            city="Kolkata",
            verification_document=SimpleUploadedFile("doc_geo.pdf", b"doc"),
            status="approved",
        )

        worker_user = User.objects.create_user(
            username="worker_geo_user",
            email="worker_geo@example.com",
            password="secret123",
            full_name="Geo Worker",
            phone="9000000019",
            role="worker",
        )
        worker = WorkerProfile.objects.create(
            user=worker_user,
            municipality=municipality,
            employee_id="W-5001",
            ward="Ward 5",
            status="available",
            is_active=True,
        )

        public_user = User.objects.create_user(
            username="public_geo_user",
            email="public_geo@example.com",
            password="secret123",
            full_name="Public Geo User",
            phone="9000000020",
            role="public",
        )
        report = WasteReport.objects.create(
            user=public_user,
            title="Street cleanup verification",
            waste_type="household",
            description="Needs closure after work.",
            urgency_level="medium",
            landmark="Community Lane",
            state="West Bengal",
            district="Kolkata",
            city="Kolkata",
            assigned_municipality=municipality,
            status="in_progress",
            assigned_worker=worker,
        )

        self.client.force_login(worker_user)
        response = self.client.post(
            reverse("complete_assigned_report", args=[report.id]),
            {"action": "resolved"},
        )

        self.assertEqual(response.status_code, 302)
        report.refresh_from_db()
        self.assertEqual(report.status, "in_progress")
        self.assertFalse(report.proof_image)
        self.assertIsNone(report.latitude)
        self.assertIsNone(report.longitude)

    def test_assignment_email_is_sent_to_worker_and_status_update_email_to_user(self):
        municipality_user = User.objects.create_user(
            username="municipality_user_4",
            email="municipality4@example.com",
            password="secret123",
            full_name="Municipality Officer Four",
            phone="9000000009",
            role="municipality",
        )
        municipality = Municipality.objects.create(
            user=municipality_user,
            organization_name="Green City 4",
            designation="Officer",
            official_email="official4@example.com",
            phone="9000000009",
            address="Main Road 4",
            state="State D",
            district="District D",
            city="City D",
            verification_document=SimpleUploadedFile("doc4.pdf", b"doc"),
            status="approved",
        )

        worker_user = User.objects.create_user(
            username="worker_user_4",
            email="worker4@example.com",
            password="secret123",
            full_name="Field Worker Four",
            phone="9000000010",
            role="worker",
        )
        worker = WorkerProfile.objects.create(
            user=worker_user,
            municipality=municipality,
            employee_id="W-4001",
            ward="Ward 4",
            status="available",
            is_active=True,
        )

        public_user = User.objects.create_user(
            username="public_user_4",
            email="public4@example.com",
            password="secret123",
            full_name="Public User Four",
            phone="9000000011",
            role="public",
        )
        report = WasteReport.objects.create(
            user=public_user,
            title="Garbage pile",
            waste_type="household",
            description="Needs cleanup.",
            urgency_level="medium",
            landmark="Town Center",
            state="State D",
            district="District D",
            city="City D",
            full_address="Town Center, District D, State D, 560001",
            latitude="12.9716",
            longitude="77.5946",
            assigned_municipality=municipality,
            status="pending",
        )

        mail.outbox = []
        self.client.force_login(municipality_user)
        self.client.post(
            reverse("municipality_assign_worker", args=[report.id]),
            {"worker": worker.id},
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [worker_user.email])
        self.assertIn("task has been assigned", mail.outbox[0].subject.lower())

        mail.outbox = []
        self.client.post(
            reverse("update_report", args=[report.id]),
            {"status": "resolved", "proof_image": ""},
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [public_user.email])
        self.assertIn("status", mail.outbox[0].subject.lower())

    def test_profile_hides_view_all_reports_for_non_public_roles(self):
        public_user = User.objects.create_user(
            username="public_profile_user",
            email="publicprofile@example.com",
            password="secret123",
            full_name="Public Profile User",
            phone="9000000015",
            role="public",
        )
        worker_user = User.objects.create_user(
            username="worker_profile_user",
            email="workerprofile@example.com",
            password="secret123",
            full_name="Worker Profile User",
            phone="9000000016",
            role="worker",
        )
        municipality_user = User.objects.create_user(
            username="municipality_profile_user",
            email="municipalityprofile@example.com",
            password="secret123",
            full_name="Officer Profile User",
            phone="9000000017",
            role="municipality",
        )

        self.client.force_login(public_user)
        public_response = self.client.get(reverse("profile"))
        self.assertContains(public_response, "View All Reports")

        self.client.force_login(worker_user)
        worker_response = self.client.get(reverse("profile"))
        self.assertNotContains(worker_response, "View All Reports")

        self.client.force_login(municipality_user)
        officer_response = self.client.get(reverse("profile"))
        self.assertNotContains(officer_response, "View All Reports")

    def test_status_rollbacks_are_blocked_and_assigned_tag_shows_for_assigned_reports(self):
        municipality_user = User.objects.create_user(
            username="municipality_user_5",
            email="municipality5@example.com",
            password="secret123",
            full_name="Municipality Officer Five",
            phone="9000000012",
            role="municipality",
        )
        municipality = Municipality.objects.create(
            user=municipality_user,
            organization_name="Green City 5",
            designation="Officer",
            official_email="official5@example.com",
            phone="9000000012",
            address="Main Road 5",
            state="State E",
            district="District E",
            city="City E",
            verification_document=SimpleUploadedFile("doc5.pdf", b"doc"),
            status="approved",
        )

        worker_user = User.objects.create_user(
            username="worker_user_5",
            email="worker5@example.com",
            password="secret123",
            full_name="Field Worker Five",
            phone="9000000013",
            role="worker",
        )
        worker = WorkerProfile.objects.create(
            user=worker_user,
            municipality=municipality,
            employee_id="W-5001",
            ward="Ward 5",
            status="available",
            is_active=True,
        )

        public_user = User.objects.create_user(
            username="public_user_5",
            email="public5@example.com",
            password="secret123",
            full_name="Public User Five",
            phone="9000000014",
            role="public",
        )
        report = WasteReport.objects.create(
            user=public_user,
            title="Garbage pile",
            waste_type="household",
            description="Needs cleanup.",
            urgency_level="medium",
            landmark="Town Center",
            state="State E",
            district="District E",
            city="City E",
            full_address="Town Center, District E, State E, 560001",
            latitude="12.9716",
            longitude="77.5946",
            assigned_municipality=municipality,
            status="resolved",
            assigned_worker=worker,
        )

        self.client.force_login(municipality_user)
        response = self.client.post(
            reverse("update_report", args=[report.id]),
            {"status": "pending", "proof_image": ""},
        )

        self.assertEqual(response.status_code, 302)
        report.refresh_from_db()
        self.assertEqual(report.status, "resolved")
        self.assertContains(self.client.get(reverse("municipality_reports")), "Assigned")
