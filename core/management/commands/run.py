import re
from datetime import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db.models import Q
from core.models import User, Project


def validate_egyptian_phone(value):
    return bool(re.match(r'^01[0-25]{1}[0-9]{8}$', value))


def validate_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M')
    except ValueError:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return None


def print_header(title):
    print('\n' + '=' * 60)
    print(f'  {title}')
    print('=' * 60)


def print_menu(options):
    for i, (key, label) in enumerate(options, 1):
        print(f'  {i}. {label}')
    print('  0. Back / Exit')


def get_menu_choice(options):
    option_list = list(options)
    while True:
        choice = input('\n  Enter your choice: ').strip()
        if choice == '0':
            return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(option_list):
                return idx
        except ValueError:
            pass
        print('  Invalid choice. Try again.')


class Command(BaseCommand):
    help = 'Crowdfunding Console App'

    def handle(self, *args, **options):
        self.user = None
        print('\n' + '#' * 60)
        print('  Welcome to Crowdfunding Console App')
        print('#' * 60)

        while True:
            if not self.user:
                self.main_menu()
            else:
                self.user_menu()

    def main_menu(self):
        print_header('Main Menu')
        options = [
            ('register', 'Register'),
            ('login', 'Login'),
            ('exit', 'Exit'),
        ]
        print_menu(options)
        choice = get_menu_choice(options)

        if choice is None:
            print('\n  Goodbye!')
            exit()

        action = options[choice][0]
        if action == 'register':
            self.register()
        elif action == 'login':
            self.login_user()
        elif action == 'exit':
            print('\n  Goodbye!')
            exit()

    def user_menu(self):
        print_header(f'Welcome {self.user.first_name} {self.user.last_name}')
        options = [
            ('create_project', 'Create Project'),
            ('view_projects', 'View All Projects'),
            ('edit_project', 'Edit My Projects'),
            ('delete_project', 'Delete My Project'),
            ('search_project', 'Search Projects by Date'),
            ('logout', 'Logout'),
        ]
        print_menu(options)
        choice = get_menu_choice(options)

        if choice is None:
            return

        action = options[choice][0]
        if action == 'create_project':
            self.create_project()
        elif action == 'view_projects':
            self.view_projects()
        elif action == 'edit_project':
            self.edit_project()
        elif action == 'delete_project':
            self.delete_project()
        elif action == 'search_project':
            self.search_project()
        elif action == 'logout':
            self.user = None
            print('\n  Logged out successfully.')

    def register(self):
        print_header('Registration')
        first_name = input('  First name: ').strip()
        last_name = input('  Last name: ').strip()
        email = input('  Email: ').strip()

        mobile_phone = input('  Mobile phone: ').strip()
        while not validate_egyptian_phone(mobile_phone):
            print('  Invalid Egyptian phone number (format: 01xxxxxxxxx)')
            mobile_phone = input('  Mobile phone: ').strip()

        password = input('  Password: ').strip()
        confirm = input('  Confirm password: ').strip()
        while password != confirm:
            print('  Passwords do not match.')
            confirm = input('  Confirm password: ').strip()

        if User.objects.filter(email=email).exists():
            print('  Email already registered.')
            return

        if User.objects.filter(mobile_phone=mobile_phone).exists():
            print('  Mobile phone already registered.')
            return

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            mobile_phone=mobile_phone,
        )
        user.is_active = True
        user.save()
        print('  Registration successful! You can now log in.')

    def login_user(self):
        print_header('Login')
        email = input('  Email: ').strip()
        password = input('  Password: ').strip()

        user = authenticate(username=email, password=password)
        if user is None:
            print('  Invalid email or password.')
            return

        if not user.is_active:
            print('  Account is not activated.')
            return

        self.user = user
        print(f'  Welcome back, {user.first_name}!')

    def create_project(self):
        print_header('Create Project')
        title = input('  Title: ').strip()
        while not title:
            title = input('  Title cannot be empty: ').strip()

        details = input('  Details: ').strip()
        target = input('  Total target (EGP): ').strip()
        while True:
            try:
                total_target = Decimal(target)
                if total_target <= 0:
                    target = input('  Target must be positive: ').strip()
                    continue
                break
            except Exception:
                target = input('  Invalid amount. Enter again: ').strip()

        start_str = input('  Start date (YYYY-MM-DD HH:MM or YYYY-MM-DD): ').strip()
        start_date = validate_date(start_str)
        while start_date is None:
            start_str = input('  Invalid date. Enter again: ').strip()
            start_date = validate_date(start_str)

        end_str = input('  End date (YYYY-MM-DD HH:MM or YYYY-MM-DD): ').strip()
        end_date = validate_date(end_str)
        while end_date is None:
            end_str = input('  Invalid date. Enter again: ').strip()
            end_date = validate_date(end_str)

        now = timezone.now()
        start_date = timezone.make_aware(start_date) if timezone.is_naive(start_date) else start_date
        end_date = timezone.make_aware(end_date) if timezone.is_naive(end_date) else end_date

        while start_date <= now:
            print('  Start date must be in the future.')
            start_str = input('  Start date (YYYY-MM-DD HH:MM): ').strip()
            start_date = validate_date(start_str)
            start_date = timezone.make_aware(start_date) if timezone.is_naive(start_date) else start_date

        while end_date <= start_date:
            print('  End date must be after start date.')
            end_str = input('  End date (YYYY-MM-DD HH:MM): ').strip()
            end_date = validate_date(end_str)
            end_date = timezone.make_aware(end_date) if timezone.is_naive(end_date) else end_date

        Project.objects.create(
            user=self.user,
            title=title,
            details=details,
            total_target=total_target,
            start_date=start_date,
            end_date=end_date,
        )
        print('  Project created successfully!')

    def view_projects(self):
        print_header('All Projects')
        projects = Project.objects.all().order_by('-created_at')
        if not projects:
            print('  No projects found.')
            return
        for p in projects:
            print(f'\n  ID: {p.id}')
            print(f'  Title: {p.title}')
            print(f'  By: {p.user.email}')
            print(f'  Target: {p.total_target} EGP')
            print(f'  Start: {p.start_date.strftime("%Y-%m-%d %H:%M")}')
            print(f'  End: {p.end_date.strftime("%Y-%m-%d %H:%M")}')
            print(f'  Details: {p.details[:100]}...' if len(p.details) > 100 else f'  Details: {p.details}')

    def edit_project(self):
        print_header('Edit My Project')
        projects = Project.objects.filter(user=self.user)
        if not projects:
            print('  You have no projects.')
            return

        for p in projects:
            print(f'  [{p.id}] {p.title}')

        pid = input('\n  Enter project ID to edit: ').strip()
        try:
            project = projects.get(id=int(pid))
        except (ValueError, Project.DoesNotExist):
            print('  Invalid project ID.')
            return

        print('  (Leave blank to keep current value)')

        title = input(f'  Title [{project.title}]: ').strip()
        if title:
            project.title = title

        details = input(f'  Details [{project.details[:30]}...]: ').strip()
        if details:
            project.details = details

        target_str = input(f'  Total target [{project.total_target}]: ').strip()
        if target_str:
            try:
                val = Decimal(target_str)
                if val <= 0:
                    print('  Target must be positive, keeping current value.')
                else:
                    project.total_target = val
            except Exception:
                print('  Invalid target, keeping current value.')

        start_str = input(f'  Start date [{project.start_date.strftime("%Y-%m-%d %H:%M")}]: ').strip()
        if start_str:
            d = validate_date(start_str)
            if d:
                d_aware = timezone.make_aware(d) if timezone.is_naive(d) else d
                if d_aware <= timezone.now():
                    print('  Start date must be in the future, keeping current value.')
                else:
                    project.start_date = d_aware
            else:
                print('  Invalid date format, keeping current value.')

        end_str = input(f'  End date [{project.end_date.strftime("%Y-%m-%d %H:%M")}]: ').strip()
        if end_str:
            d = validate_date(end_str)
            if d:
                d_aware = timezone.make_aware(d) if timezone.is_naive(d) else d
                if d_aware <= project.start_date:
                    print('  End date must be after start date, keeping current value.')
                else:
                    project.end_date = d_aware
            else:
                print('  Invalid date format, keeping current value.')

        project.save()
        print('  Project updated!')

    def delete_project(self):
        print_header('Delete My Project')
        projects = Project.objects.filter(user=self.user)
        if not projects:
            print('  You have no projects.')
            return

        for p in projects:
            print(f'  [{p.id}] {p.title}')

        pid = input('\n  Enter project ID to delete: ').strip()
        try:
            project = projects.get(id=int(pid))
        except (ValueError, Project.DoesNotExist):
            print('  Invalid project ID.')
            return

        confirm = input(f'  Are you sure you want to delete "{project.title}"? (y/n): ').strip().lower()
        if confirm == 'y':
            project.delete()
            print('  Project deleted.')
        else:
            print('  Cancelled.')

    def search_project(self):
        print_header('Search Projects by Date')
        start_str = input('  From date (YYYY-MM-DD): ').strip()
        end_str = input('  To date (YYYY-MM-DD): ').strip()

        start_date = validate_date(start_str) if start_str else None
        end_date = validate_date(end_str) if end_str else None

        q = Q()
        if start_date:
            start_date = timezone.make_aware(start_date) if timezone.is_naive(start_date) else start_date
            q &= Q(start_date__gte=start_date)
        if end_date:
            end_date = timezone.make_aware(end_date) if timezone.is_naive(end_date) else end_date
            q &= Q(end_date__lte=end_date)

        projects = Project.objects.filter(q).order_by('start_date')
        if not projects:
            print('  No projects found in this date range.')
            return

        for p in projects:
            print(f'\n  [{p.id}] {p.title}')
            print(f'  Target: {p.total_target} EGP')
            print(f'  Period: {p.start_date.strftime("%Y-%m-%d")} to {p.end_date.strftime("%Y-%m-%d")}')
