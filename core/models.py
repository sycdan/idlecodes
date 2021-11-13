from django.db import models


class Promotion(models.Model):
  code = models.CharField(max_length=250)
  expires_at = models.DateTimeField(blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.code

  class Meta:
    ordering = ['-created_at']


class Platform(models.Model):
  key = models.CharField(max_length=50)
  hash = models.CharField(max_length=250)
  user_id = models.CharField(max_length=100)
  instance_id = models.CharField(max_length=100, blank=True, null=True)

  def __str__(self):
    return self.key


class Redemption(models.Model):
  promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE)
  platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
  created_at = models.DateTimeField(auto_now_add=True)
  message = models.TextField(blank=True, null=True)

  def __str__(self):
    return f"{self.platform.key}|{self.promotion.code}"

  class Meta:
    unique_together = [['promotion', 'platform']]
    ordering = ['-created_at']
