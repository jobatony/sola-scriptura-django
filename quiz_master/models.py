from django.db import models
from django.contrib.auth.models import User
from registration_and_settings.models import Competition

# List of all 66 books of the Bible for dropdown choices
BIBLE_BOOKS = [
    ('Genesis', 'Genesis'), ('Exodus', 'Exodus'), ('Leviticus', 'Leviticus'), ('Numbers', 'Numbers'), ('Deuteronomy', 'Deuteronomy'),
    ('Joshua', 'Joshua'), ('Judges', 'Judges'), ('Ruth', 'Ruth'), ('1 Samuel', '1 Samuel'), ('2 Samuel', '2 Samuel'),
    ('1 Kings', '1 Kings'), ('2 Kings', '2 Kings'), ('1 Chronicles', '1 Chronicles'), ('2 Chronicles', '2 Chronicles'),
    ('Ezra', 'Ezra'), ('Nehemiah', 'Nehemiah'), ('Esther', 'Esther'), ('Job', 'Job'), ('Psalms', 'Psalms'), ('Proverbs', 'Proverbs'),
    ('Ecclesiastes', 'Ecclesiastes'), ('Song of Solomon', 'Song of Solomon'), ('Isaiah', 'Isaiah'), ('Jeremiah', 'Jeremiah'),
    ('Lamentations', 'Lamentations'), ('Ezekiel', 'Ezekiel'), ('Daniel', 'Daniel'), ('Hosea', 'Hosea'), ('Joel', 'Joel'),
    ('Amos', 'Amos'), ('Obadiah', 'Obadiah'), ('Jonah', 'Jonah'), ('Micah', 'Micah'), ('Nahum', 'Nahum'), ('Habakkuk', 'Habakkuk'),
    ('Zephaniah', 'Zephaniah'), ('Haggai', 'Haggai'), ('Zechariah', 'Zechariah'), ('Malachi', 'Malachi'),
    ('Matthew', 'Matthew'), ('Mark', 'Mark'), ('Luke', 'Luke'), ('John', 'John'), ('Acts', 'Acts'),
    ('Romans', 'Romans'), ('1 Corinthians', '1 Corinthians'), ('2 Corinthians', '2 Corinthians'), ('Galatians', 'Galatians'),
    ('Ephesians', 'Ephesians'), ('Philippians', 'Philippians'), ('Colossians', 'Colossians'),
    ('1 Thessalonians', '1 Thessalonians'), ('2 Thessalonians', '2 Thessalonians'), ('1 Timothy', '1 Timothy'),
    ('2 Timothy', '2 Timothy'), ('Titus', 'Titus'), ('Philemon', 'Philemon'), ('Hebrews', 'Hebrews'), ('James', 'James'),
    ('1 Peter', '1 Peter'), ('2 Peter', '2 Peter'), ('1 John', '1 John'), ('2 John', '2 John'), ('3 John', '3 John'),
    ('Jude', 'Jude'), ('Revelation', 'Revelation')
]

class BibleQuestion(models.Model):
    verse_text = models.TextField()
    correct_book = models.CharField(max_length=50, choices=BIBLE_BOOKS)
    wrong_option_1 = models.CharField(max_length=50, choices=BIBLE_BOOKS)
    wrong_option_2 = models.CharField(max_length=50, choices=BIBLE_BOOKS)
    wrong_option_3 = models.CharField(max_length=50, choices=BIBLE_BOOKS)
    chapter = models.IntegerField(null=True, blank=True)
    verse = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.correct_book} {self.chapter}:{self.verse} (Q: {self.verse_text[:30]}...)"
    

class CompetitorState(models.Model):
    STATE_CHOICES = [
        ('qualified', 'Qualified'),
        ('disqualified', 'Disqualified'),
    ]

    # We link to the specific Competition
    competition = models.ForeignKey(
        'registration_and_settings.Competition', 
        on_delete=models.CASCADE,
        related_name='competitor_states'
    )
    
    # Unique identifier for the participant
    participant_access_code = models.CharField(max_length=10)
    
    # The current status
    state = models.CharField(
        max_length=20, 
        choices=STATE_CHOICES, 
        default='qualified'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure a participant can't have duplicate states in the same competition
        unique_together = ('competition', 'participant_access_code')

    def __str__(self):
        return f"{self.participant_access_code} - {self.state}"
    
class GameTracker(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    round_number = models.IntegerField()
    # Stores [12, 45, 2, 8, 99, 101] - The exact IDs of the 6 questions
    generated_questions = models.JSONField(default=list) 
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comp {self.competition.id} - Round {self.round_number}"
    
class ParticipantResponse(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    participant_access_code = models.CharField(max_length=10)
    round_number = models.IntegerField()
    
    question = models.ForeignKey(BibleQuestion, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=100)
    
    # Store validation results
    is_correct = models.BooleanField(default=False)
    correct_answer_ref = models.CharField(max_length=100) # Snapshot of what was correct
    
    time_taken = models.FloatField(help_text="Time in seconds")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.participant_access_code} - R{self.round_number} - {self.is_correct}"