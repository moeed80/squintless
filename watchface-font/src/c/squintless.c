#include <pebble.h>

#include "generated/squintless_typeface_assets.h"

typedef struct {
  int outer_margin;
  int central_gap_h;
  int battery_line_h;
  int battery_line_inset;
  int low_battery_min_w;
  GRect hour_bounds;
  GRect minute_bounds;
  GRect battery_bounds;
} SquintlessLayout;

static Window *s_window;
static Layer *s_face_layer;
static GBitmap *s_hour_bitmap;
static GBitmap *s_minute_bitmap;
static char s_hour_text[4];
static char s_minute_text[4];
static int s_battery_percent = 100;

static SquintlessLayout prv_layout_for_bounds(GRect bounds) {
  const int outer_margin = 2;
  const int central_gap_h = 16;
  const int battery_line_h = 7;
  const int battery_line_inset = 5;
  const int half_h = (bounds.size.h - central_gap_h) / 2;
  const int gap_y = bounds.origin.y + half_h;
  const int line_y = gap_y + (central_gap_h - battery_line_h) / 2;

  return (SquintlessLayout) {
    .outer_margin = outer_margin,
    .central_gap_h = central_gap_h,
    .battery_line_h = battery_line_h,
    .battery_line_inset = battery_line_inset,
    .low_battery_min_w = 8,
    .hour_bounds = GRect(bounds.origin.x + outer_margin,
                         bounds.origin.y,
                         bounds.size.w - (outer_margin * 2),
                         half_h),
    .minute_bounds = GRect(bounds.origin.x + outer_margin,
                           gap_y + central_gap_h,
                           bounds.size.w - (outer_margin * 2),
                           bounds.size.h - half_h - central_gap_h),
    .battery_bounds = GRect(bounds.origin.x + battery_line_inset,
                            line_y,
                            bounds.size.w - (battery_line_inset * 2),
                            battery_line_h),
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

static void prv_update_time_assets(void) {
  char hour_text[4];
  char minute_text[4];

  prv_get_time_text(hour_text, sizeof(hour_text), minute_text, sizeof(minute_text));
  prv_replace_bitmap_if_needed(&s_hour_bitmap, s_hour_text, hour_text);
  prv_replace_bitmap_if_needed(&s_minute_bitmap, s_minute_text, minute_text);
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

static void prv_draw_battery(GContext *ctx, const SquintlessLayout *layout) {
  int fill_w = (layout->battery_bounds.size.w * s_battery_percent) / 100;
  if (s_battery_percent > 0 && fill_w < layout->low_battery_min_w) {
    fill_w = layout->low_battery_min_w;
  }

  graphics_context_set_fill_color(ctx, GColorLightGray);
  graphics_fill_rect(ctx, layout->battery_bounds, 0, GCornersAll);

  if (fill_w > 0) {
    graphics_context_set_fill_color(ctx, GColorBlack);
    graphics_fill_rect(ctx, GRect(layout->battery_bounds.origin.x,
                                  layout->battery_bounds.origin.y,
                                  fill_w,
                                  layout->battery_bounds.size.h),
                       0, GCornersAll);
  }
}

static void prv_face_update_proc(Layer *layer, GContext *ctx) {
  GRect bounds = layer_get_bounds(layer);
  SquintlessLayout layout = prv_layout_for_bounds(bounds);

  graphics_context_set_fill_color(ctx, GColorWhite);
  graphics_fill_rect(ctx, bounds, 0, GCornersAll);

  prv_draw_bitmap_centered(ctx, s_hour_bitmap, layout.hour_bounds);
  prv_draw_battery(ctx, &layout);
  prv_draw_bitmap_centered(ctx, s_minute_bitmap, layout.minute_bounds);
}

static void prv_tick_handler(struct tm *tick_time, TimeUnits units_changed) {
  prv_update_time_assets();
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
  battery_state_service_subscribe(prv_battery_handler);
  tick_timer_service_subscribe(MINUTE_UNIT, prv_tick_handler);

  window_stack_push(s_window, false);
}

static void prv_deinit(void) {
  tick_timer_service_unsubscribe();
  battery_state_service_unsubscribe();
  if (s_hour_bitmap) {
    gbitmap_destroy(s_hour_bitmap);
  }
  if (s_minute_bitmap) {
    gbitmap_destroy(s_minute_bitmap);
  }
  window_destroy(s_window);
}

int main(void) {
  prv_init();
  app_event_loop();
  prv_deinit();
}
