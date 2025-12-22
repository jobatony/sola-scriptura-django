from django.db import models
from django.contrib.auth.models import User

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