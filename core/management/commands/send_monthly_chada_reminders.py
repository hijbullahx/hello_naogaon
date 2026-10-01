import calendar
from datetime import date
from django.core.management.base import BaseCommand
from volunteers.models import TeamMember
from volunteers.subscription_services import (
    get_member_subscription_summary,
    send_member_monthly_reminder,
    send_all_existing_members_update,
)

class Command(BaseCommand):
    help = 'Send monthly chada fee reminders (or notify all existing members with --all)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Send updated fee & due status notification to ALL core members right now',
        )
        parser.add_argument(
            '--member-id',
            type=str,
            help='Send notification to a specific member ID',
        )

    def handle(self, *args, **options):
        send_all = options.get('all')
        member_id = options.get('member_id')
        today = date.today()

        if send_all:
            self.stdout.write(self.style.NOTICE("Sending updated fee & due status notification to ALL existing core members..."))
            results = send_all_existing_members_update()
            for r in results:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Notified: {r['name']} ({r['member_id']}) | Fee: BDT {r['monthly_fee']} | Due: BDT {r['due_amount']} | SMS: {r['sms_sent']} | Email: {r['email_sent']}"
                    )
                )
            self.stdout.write(self.style.SUCCESS(f"Successfully processed {len(results)} members."))
            return

        if member_id:
            member = TeamMember.objects.filter(member_id__iexact=member_id).first()
            if not member:
                self.stdout.write(self.style.ERROR(f"Member with ID '{member_id}' not found."))
                return
            self.stdout.write(self.style.NOTICE(f"Sending monthly reminder to {member.name} ({member.member_id})..."))
            send_member_monthly_reminder(member, today=today)
            self.stdout.write(self.style.SUCCESS(f"Notification sent to {member.name}."))
            return

        # Daily scheduled cron mode: Find members whose billing day is today
        members = TeamMember.objects.all().order_by('order', 'name')
        max_days_this_month = calendar.monthrange(today.year, today.month)[1]
        notified_count = 0

        self.stdout.write(self.style.NOTICE(f"Checking scheduled monthly chada reminders for today ({today.strftime('%d-%m-%Y')})..."))

        for mem in members:
            join_date = mem.created_at.date() if mem.created_at else today
            target_day = min(join_date.day, max_days_this_month)

            if today.day == target_day:
                summary = get_member_subscription_summary(mem, today=today)
                self.stdout.write(
                    f"Triggering monthly billing reminder for {mem.name} ({mem.member_id}) - Due: BDT {summary['due_amount']}"
                )
                send_member_monthly_reminder(mem, today=today)
                notified_count += 1

        self.stdout.write(self.style.SUCCESS(f"Finished daily check. Notified {notified_count} member(s)."))
