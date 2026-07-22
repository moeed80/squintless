#include <pebble.h>

#include "generated/squintless_date_assets.h"
#include "generated/squintless_typeface_assets.h"

#define DATE_GLANCE_MS 3000

typedef struct {
  int outer_margin;
  int central_gap_h;
  int battery_bar_h;
  int battery_bar_inset;
  int battery_bar_radius;
  int battery_bar_border;
  GRect hour_bounds;
  GRect minute_bounds;
  GRect battery_bounds;
} SquintlessLayout;

static Window *s_window;
static Layer *s_face_layer;
static GBitmap *s_hour_bitmap;
static GBitmap *s_minute_bitmap;
#if defined(PBL_PLATFORM_APLITE)
static GBitmap *s_hour_second_bitmap;
static GBitmap *s_minute_second_bitmap;
#endif
static GBitmap *s_date_month_bitmap;
static GBitmap *s_date_day_bitmap;
static AppTimer *s_date_timer;
static char s_hour_text[4];
static char s_minute_text[4];
static int s_date_month_index;
static int s_date_day_index;
static int s_battery_percent = 100;
static bool s_showing_date;

static SquintlessLayout prv_layout_for_bounds(GRect bounds) {
  const bool is_144_rect = bounds.size.w == 144 && bounds.size.h == 168;
  const int outer_margin = 2;
  const int central_gap_h = is_144_rect ? 14 : 16;
  const int battery_bar_h = is_144_rect ? 7 : 9;
  const int battery_bar_inset = is_144_rect ? 4 : 5;
  const int battery_bar_radius = 2;
  const int battery_bar_border = 1;
  const int half_h = (bounds.size.h - central_gap_h) / 2;
  const int gap_y = bounds.origin.y + half_h;
  const int bar_y = gap_y + (central_gap_h - battery_bar_h) / 2;

  return (SquintlessLayout) {
    .outer_margin = outer_margin,
    .central_gap_h = central_gap_h,
    .battery_bar_h = battery_bar_h,
    .battery_bar_inset = battery_bar_inset,
    .battery_bar_radius = battery_bar_radius,
    .battery_bar_border = battery_bar_border,
    .hour_bounds = GRect(bounds.origin.x + outer_margin,
                         bounds.origin.y,
                         bounds.size.w - (outer_margin * 2),
                         half_h),
    .minute_bounds = GRect(bounds.origin.x + outer_margin,
                           gap_y + central_gap_h,
                           bounds.size.w - (outer_margin * 2),
                           bounds.size.h - half_h - central_gap_h),
    .battery_bounds = GRect(bounds.origin.x + battery_bar_inset,
                            bar_y,
                            bounds.size.w - (battery_bar_inset * 2),
                            battery_bar_h),
  };
}

static void prv_get_time_text(char *hour_text, size_t hour_text_size,
                              char *minute_text, size_t minute_text_size) {
  time_t now = time(NULL);
  struct tm *tick_time = localtime(&now);
  const int hour_24 = tick_time->tm_hour;

  if (clock_is_24h_style()) {
    snprintf(hour_text, hour_text_size, "%02d", hour_24);
  } else {
    int hour_12 = hour_24 % 12;
    if (hour_12 == 0) {
      hour_12 = 12;
    }
    snprintf(hour_text, hour_text_size, "%d", hour_12);
  }
  snprintf(minute_text, minute_text_size, "%02d", tick_time->tm_min);
}

static void prv_get_date_indices(int *month_index, int *day_index) {
  time_t now = time(NULL);
  struct tm *tick_time = localtime(&now);
  int month = tick_time->tm_mon + 1;
  int day = tick_time->tm_mday;

  if (month < 1) {
    month = 1;
  } else if (month > 12) {
    month = 12;
  }

  if (day < 1) {
    day = 1;
  } else if (day > 31) {
    day = 31;
  }

  *month_index = month - 1;
  *day_index = day - 1;
}

#if !defined(PBL_PLATFORM_APLITE)
static uint32_t prv_resource_id_for_text(const char *text) {
  const size_t len = strlen(text);
  if (len == 1) {
    return SQUINTLESS_SINGLE_RESOURCE_IDS[text[0] - '0'];
  }

  const uint8_t pair_index = squintless_pair_index(text[0], text[1]);
  return SQUINTLESS_PAIR_RESOURCE_IDS[pair_index];
}

static void prv_replace_bitmap_if_needed(GBitmap **bitmap, char *cached_text,
                                         const char *new_text) {
  if (strcmp(cached_text, new_text) == 0 && *bitmap) {
    return;
  }

  if (*bitmap) {
    gbitmap_destroy(*bitmap);
  }

  *bitmap = gbitmap_create_with_resource(prv_resource_id_for_text(new_text));
  strncpy(cached_text, new_text, 3);
  cached_text[3] = '\0';
}
#endif

#if defined(PBL_PLATFORM_APLITE)
static void prv_replace_digit_bitmaps_if_needed(GBitmap **first_bitmap,
                                                GBitmap **second_bitmap,
                                                char *cached_text,
                                                const char *new_text) {
  if (strcmp(cached_text, new_text) == 0 && *first_bitmap) {
    return;
  }

  if (*first_bitmap) {
    gbitmap_destroy(*first_bitmap);
  }
  if (*second_bitmap) {
    gbitmap_destroy(*second_bitmap);
    *second_bitmap = NULL;
  }

  *first_bitmap = gbitmap_create_with_resource(
      SQUINTLESS_SINGLE_RESOURCE_IDS[new_text[0] - '0']);

  if (strlen(new_text) == 2) {
    *second_bitmap = gbitmap_create_with_resource(
        SQUINTLESS_SINGLE_RESOURCE_IDS[new_text[1] - '0']);
  }

  strncpy(cached_text, new_text, 3);
  cached_text[3] = '\0';
}
#endif

static void prv_replace_resource_bitmap_if_needed(GBitmap **bitmap, int *cached_index,
                                                  int new_index, uint32_t resource_id) {
  if (*cached_index == new_index && *bitmap) {
    return;
  }

  if (*bitmap) {
    gbitmap_destroy(*bitmap);
  }

  *bitmap = gbitmap_create_with_resource(resource_id);
  *cached_index = new_index;
}

static void prv_update_time_assets(void) {
  char hour_text[4];
  char minute_text[4];

  prv_get_time_text(hour_text, sizeof(hour_text), minute_text, sizeof(minute_text));
#if defined(PBL_PLATFORM_APLITE)
  prv_replace_digit_bitmaps_if_needed(
      &s_hour_bitmap,
      &s_hour_second_bitmap,
      s_hour_text,
      hour_text);
  prv_replace_digit_bitmaps_if_needed(
      &s_minute_bitmap,
      &s_minute_second_bitmap,
      s_minute_text,
      minute_text);
#else
  prv_replace_bitmap_if_needed(&s_hour_bitmap, s_hour_text, hour_text);
  prv_replace_bitmap_if_needed(&s_minute_bitmap, s_minute_text, minute_text);
#endif
}

static void prv_update_date_assets(void) {
  int month_index;
  int day_index;

  prv_get_date_indices(&month_index, &day_index);
  prv_replace_resource_bitmap_if_needed(
      &s_date_month_bitmap,
      &s_date_month_index,
      month_index,
      SQUINTLESS_DATE_MONTH_RESOURCE_IDS[month_index]);
  prv_replace_resource_bitmap_if_needed(
      &s_date_day_bitmap,
      &s_date_day_index,
      day_index,
      SQUINTLESS_DATE_DAY_RESOURCE_IDS[day_index]);
}

static void prv_draw_bitmap_centered(GContext *ctx, GBitmap *bitmap, GRect bounds) {
  if (!bitmap) {
    return;
  }

  const GRect bitmap_bounds = gbitmap_get_bounds(bitmap);
  const int x = bounds.origin.x + ((bounds.size.w - bitmap_bounds.size.w) / 2);
  const int y = bounds.origin.y + ((bounds.size.h - bitmap_bounds.size.h) / 2);
  graphics_draw_bitmap_in_rect(ctx, bitmap,
                               GRect(x, y, bitmap_bounds.size.w, bitmap_bounds.size.h));
}

#if defined(PBL_PLATFORM_APLITE)
static void prv_draw_digit_bitmaps_centered(GContext *ctx, const char *text,
                                            GBitmap *first_bitmap,
                                            GBitmap *second_bitmap,
                                            GRect bounds) {
  if (!first_bitmap) {
    return;
  }

  if (strlen(text) == 1 || !second_bitmap) {
    prv_draw_bitmap_centered(ctx, first_bitmap, bounds);
    return;
  }

  const GRect first_bounds = gbitmap_get_bounds(first_bitmap);
  const GRect second_bounds = gbitmap_get_bounds(second_bitmap);
  int spacing = squintless_pair_spacing(text[0], text[1]);
  if (spacing < 0) {
    spacing = 0;
  }
  const int total_w = first_bounds.size.w + spacing + second_bounds.size.w;
  const int row_h = first_bounds.size.h > second_bounds.size.h ?
                    first_bounds.size.h : second_bounds.size.h;
  const int x = bounds.origin.x + ((bounds.size.w - total_w) / 2);
  const int y = bounds.origin.y + ((bounds.size.h - row_h) / 2);

  graphics_draw_bitmap_in_rect(ctx,
                               first_bitmap,
                               GRect(x,
                                     y + ((row_h - first_bounds.size.h) / 2),
                                     first_bounds.size.w,
                                     first_bounds.size.h));
  graphics_draw_bitmap_in_rect(ctx,
                               second_bitmap,
                               GRect(x + first_bounds.size.w + spacing,
                                     y + ((row_h - second_bounds.size.h) / 2),
                                     second_bounds.size.w,
                                     second_bounds.size.h));
}
#endif

static void prv_draw_battery(GContext *ctx, const SquintlessLayout *layout) {
  const GRect outer = layout->battery_bounds;
  const int border = layout->battery_bar_border;
  const int inner_radius = layout->battery_bar_radius > border ?
                           layout->battery_bar_radius - border : 0;
  const GRect inner = GRect(outer.origin.x + border,
                            outer.origin.y + border,
                            outer.size.w - (border * 2),
                            outer.size.h - (border * 2));
  int fill_w = (inner.size.w * s_battery_percent + 50) / 100;
  if (fill_w > inner.size.w) {
    fill_w = inner.size.w;
  }

  graphics_context_set_fill_color(ctx, GColorBlack);
  graphics_fill_rect(ctx, outer, layout->battery_bar_radius, GCornersAll);

  graphics_context_set_fill_color(ctx, GColorWhite);
  graphics_fill_rect(ctx, inner, inner_radius, GCornersAll);

  if (fill_w > 0) {
    graphics_context_set_fill_color(ctx, GColorBlack);
    graphics_fill_rect(ctx, GRect(inner.origin.x,
                                  inner.origin.y,
                                  fill_w,
                                  inner.size.h),
                       inner_radius,
                       fill_w >= inner.size.w ? GCornersAll :
                                                (GCornerTopLeft | GCornerBottomLeft));
  }
}

static void prv_draw_date_separator(GContext *ctx, const SquintlessLayout *layout) {
  const GRect bounds = layout->battery_bounds;
  const int center_x = bounds.origin.x + (bounds.size.w / 2);
  const int top_y = bounds.origin.y - 1;
  const int bottom_y = bounds.origin.y + bounds.size.h;
  const int stroke_w = layout->battery_bar_h <= 7 ? 2 : 3;
  const int x_offset = layout->battery_bar_h <= 7 ? 4 : 5;

  graphics_context_set_stroke_color(ctx, GColorBlack);
  graphics_context_set_stroke_width(ctx, stroke_w);
  graphics_draw_line(ctx, GPoint(center_x + x_offset, top_y),
                     GPoint(center_x - x_offset, bottom_y));
  graphics_context_set_stroke_width(ctx, 1);
}

static void prv_face_update_proc(Layer *layer, GContext *ctx) {
  GRect bounds = layer_get_bounds(layer);
  SquintlessLayout layout = prv_layout_for_bounds(bounds);

  graphics_context_set_fill_color(ctx, GColorWhite);
  graphics_fill_rect(ctx, bounds, 0, GCornersAll);

  if (s_showing_date) {
    prv_draw_bitmap_centered(ctx, s_date_month_bitmap, layout.hour_bounds);
    prv_draw_date_separator(ctx, &layout);
    prv_draw_bitmap_centered(ctx, s_date_day_bitmap, layout.minute_bounds);
  } else {
#if defined(PBL_PLATFORM_APLITE)
    prv_draw_digit_bitmaps_centered(ctx,
                                    s_hour_text,
                                    s_hour_bitmap,
                                    s_hour_second_bitmap,
                                    layout.hour_bounds);
    prv_draw_battery(ctx, &layout);
    prv_draw_digit_bitmaps_centered(ctx,
                                    s_minute_text,
                                    s_minute_bitmap,
                                    s_minute_second_bitmap,
                                    layout.minute_bounds);
#else
    prv_draw_bitmap_centered(ctx, s_hour_bitmap, layout.hour_bounds);
    prv_draw_battery(ctx, &layout);
    prv_draw_bitmap_centered(ctx, s_minute_bitmap, layout.minute_bounds);
#endif
  }
}

static void prv_hide_date_timer_callback(void *context) {
  s_date_timer = NULL;
  s_showing_date = false;
  if (s_face_layer) {
    layer_mark_dirty(s_face_layer);
  }
}

static void prv_show_date_glance(void) {
  prv_update_date_assets();
  s_showing_date = true;

  if (s_date_timer) {
    app_timer_cancel(s_date_timer);
  }
  s_date_timer = app_timer_register(DATE_GLANCE_MS, prv_hide_date_timer_callback, NULL);

  if (s_face_layer) {
    layer_mark_dirty(s_face_layer);
  }
}

static void prv_accel_tap_handler(AccelAxisType axis, int32_t direction) {
  prv_show_date_glance();
}

static void prv_tick_handler(struct tm *tick_time, TimeUnits units_changed) {
  prv_update_time_assets();
  if (s_showing_date) {
    prv_update_date_assets();
  }
  if (s_face_layer) {
    layer_mark_dirty(s_face_layer);
  }
}

static void prv_battery_handler(BatteryChargeState state) {
  const int clamped_percent = state.charge_percent > 100 ? 100 :
                              state.charge_percent;
  if (clamped_percent != s_battery_percent) {
    s_battery_percent = clamped_percent;
    if (s_face_layer) {
      layer_mark_dirty(s_face_layer);
    }
  }
}

static void prv_window_load(Window *window) {
  Layer *window_layer = window_get_root_layer(window);
  GRect bounds = layer_get_bounds(window_layer);

  s_face_layer = layer_create(bounds);
  layer_set_update_proc(s_face_layer, prv_face_update_proc);
  layer_add_child(window_layer, s_face_layer);
}

static void prv_window_unload(Window *window) {
  layer_destroy(s_face_layer);
  s_face_layer = NULL;
}

static void prv_init(void) {
  s_window = window_create();
  window_set_background_color(s_window, GColorWhite);
  window_set_window_handlers(s_window, (WindowHandlers) {
    .load = prv_window_load,
    .unload = prv_window_unload,
  });

  BatteryChargeState initial_battery = battery_state_service_peek();
  s_battery_percent = initial_battery.charge_percent;
  prv_update_time_assets();
  accel_tap_service_subscribe(prv_accel_tap_handler);
  battery_state_service_subscribe(prv_battery_handler);
  tick_timer_service_subscribe(MINUTE_UNIT, prv_tick_handler);

  window_stack_push(s_window, false);
}

static void prv_deinit(void) {
  tick_timer_service_unsubscribe();
  battery_state_service_unsubscribe();
  accel_tap_service_unsubscribe();
  if (s_date_timer) {
    app_timer_cancel(s_date_timer);
    s_date_timer = NULL;
  }
  if (s_hour_bitmap) {
    gbitmap_destroy(s_hour_bitmap);
  }
  if (s_minute_bitmap) {
    gbitmap_destroy(s_minute_bitmap);
  }
#if defined(PBL_PLATFORM_APLITE)
  if (s_hour_second_bitmap) {
    gbitmap_destroy(s_hour_second_bitmap);
  }
  if (s_minute_second_bitmap) {
    gbitmap_destroy(s_minute_second_bitmap);
  }
#endif
  if (s_date_month_bitmap) {
    gbitmap_destroy(s_date_month_bitmap);
  }
  if (s_date_day_bitmap) {
    gbitmap_destroy(s_date_day_bitmap);
  }
  window_destroy(s_window);
}

int main(void) {
  prv_init();
  app_event_loop();
  prv_deinit();
}
