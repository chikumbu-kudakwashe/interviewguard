from core.management.commands.seed_interview_questions import Command as SeedInterviewQuestionsCommand


class Command(SeedInterviewQuestionsCommand):
    help = "Seed reusable InterviewGuard data, including approved interview questions and CV builders."
