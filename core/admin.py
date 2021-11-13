from django.contrib import admin

from core.models import Platform, Promotion, Redemption


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
  list_display = (
    '__str__',
    'created_at',
  )


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
  list_display = (
    '__str__',
    'hash',
    'user_id',
  )


@admin.register(Redemption)
class RedemptionAdmin(admin.ModelAdmin):
  list_display = (
    '__str__',
    'message',
    'created_at',
  )
  list_filter = (
    'platform__key',
    'promotion__code',
  )
