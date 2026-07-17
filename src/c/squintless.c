#include <pebble.h>

enum {
  PT2_WIDTH = 200,
  PT2_HEIGHT = 228,
  DIGIT_UNITS_W = 13,
  DIGIT_UNITS_H = 15,
  SOLID_ONE_UNITS_W = 11,
};

#define SQUINTLESS_STYLE_SEGMENTED 1
#define SQUINTLESS_STYLE_SOLID 2

#ifndef SQUINTLESS_NUMERAL_STYLE
#define SQUINTLESS_NUMERAL_STYLE SQUINTLESS_STYLE_SOLID
#endif

typedef struct {
  int outer_margin;
  int central_gap_h;
  int battery_line_h;
  int battery_line_inset;
  int default_digit_spacing_units;
  int digit_corner_radius;
  int low_battery_min_w;
  GRect hour_bounds;
  GRect minute_bounds;
  GRect battery_bounds;
} SquintlessLayout;

static Window *s_window;
static Layer *s_face_layer;
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
    .default_digit_spacing_units = 1,
    .digit_corner_radius = 2,
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

static void prv_fill_scaled_rect(GContext *ctx, GPoint origin, int scale, int radius,
                                 int x, int y, int w, int h) {
  graphics_fill_rect(ctx, GRect(origin.x + (x * scale),
                                origin.y + (y * scale),
                                w * scale,
                                h * scale),
                     radius, GCornersAll);
}

static void prv_fill_scaled_rect_color(GContext *ctx, GColor color, GPoint origin,
                                       int scale, int radius, int x, int y,
                                       int w, int h) {
  graphics_context_set_fill_color(ctx, color);
  prv_fill_scaled_rect(ctx, origin, scale, radius, x, y, w, h);
}

static void prv_solid_black(GContext *ctx, GPoint origin, int scale, int radius,
                            int x, int y, int w, int h) {
  prv_fill_scaled_rect_color(ctx, GColorBlack, origin, scale, radius, x, y, w, h);
}

static void prv_solid_white(GContext *ctx, GPoint origin, int scale, int radius,
                            int x, int y, int w, int h) {
  prv_fill_scaled_rect_color(ctx, GColorWhite, origin, scale, radius, x, y, w, h);
}

static void __attribute__((unused)) prv_draw_solid_digit(GContext *ctx, char digit,
                                                         GPoint origin, int scale,
                                                         int radius) {
  const int inner_radius = radius / 2;

  switch (digit) {
    case '0':
      prv_solid_black(ctx, origin, scale, radius, 0, 0, 13, 15);
      prv_solid_white(ctx, origin, scale, inner_radius, 4, 3, 5, 9);
      break;
    case '1':
      prv_solid_black(ctx, origin, scale, radius, 1, 0, 8, 4);
      prv_solid_black(ctx, origin, scale, radius, 4, 0, 5, 15);
      prv_solid_black(ctx, origin, scale, radius, 0, 11, 11, 4);
      break;
    case '2':
      prv_solid_black(ctx, origin, scale, radius, 0, 0, 13, 15);
      prv_solid_white(ctx, origin, scale, inner_radius, 0, 4, 7, 3);
      prv_solid_white(ctx, origin, scale, inner_radius, 6, 9, 7, 3);
      break;
    case '3':
      prv_solid_black(ctx, origin, scale, radius, 0, 0, 13, 15);
      prv_solid_white(ctx, origin, scale, inner_radius, 0, 3, 8, 3);
      prv_solid_white(ctx, origin, scale, inner_radius, 0, 9, 8, 3);
      break;
    case '4':
      prv_solid_black(ctx, origin, scale, radius, 0, 0, 4, 9);
      prv_solid_black(ctx, origin, scale, radius, 8, 0, 5, 15);
      prv_solid_black(ctx, origin, scale, radius, 0, 6, 13, 4);
      break;
    case '5':
      prv_solid_black(ctx, origin, scale, radius, 0, 0, 13, 15);
      prv_solid_white(ctx, origin, scale, inner_radius, 6, 4, 7, 3);
      prv_solid_white(ctx, origin, scale, inner_radius, 0, 9, 7, 3);
      break;
    case '6':
      prv_solid_black(ctx, origin, scale, radius, 0, 0, 13, 15);
      prv_solid_white(ctx, origin, scale, inner_radius, 5, 3, 8, 3);
      prv_solid_white(ctx, origin, scale, inner_radius, 4, 9, 5, 3);
      break;
    case '7':
      prv_solid_black(ctx, origin, scale, radius, 0, 0, 13, 4);
      prv_solid_black(ctx, origin, scale, radius, 8, 3, 5, 4);
      prv_solid_black(ctx, origin, scale, radius, 6, 6, 5, 4);
      prv_solid_black(ctx, origin, scale, radius, 4, 9, 5, 6);
      break;
    case '8':
      prv_solid_black(ctx, origin, scale, radius, 0, 0, 13, 15);
      prv_solid_white(ctx, origin, scale, inner_radius, 4, 3, 5, 3);
      prv_solid_white(ctx, origin, scale, inner_radius, 4, 9, 5, 3);
      break;
    case '9':
      prv_solid_black(ctx, origin, scale, radius, 0, 0, 13, 15);
      prv_solid_white(ctx, origin, scale, inner_radius, 4, 3, 5, 3);
      prv_solid_white(ctx, origin, scale, inner_radius, 0, 9, 8, 3);
      break;
  }

  graphics_context_set_fill_color(ctx, GColorBlack);
}

static void prv_segment_top(GContext *ctx, GPoint o, int s, int r) {
  prv_fill_scaled_rect(ctx, o, s, r, 3, 0, 7, 3);
}

static void prv_segment_upper_left(GContext *ctx, GPoint o, int s, int r) {
  prv_fill_scaled_rect(ctx, o, s, r, 0, 2, 3, 6);
}

static void prv_segment_upper_right(GContext *ctx, GPoint o, int s, int r) {
  prv_fill_scaled_rect(ctx, o, s, r, 10, 2, 3, 6);
}

static void prv_segment_middle(GContext *ctx, GPoint o, int s, int r) {
  prv_fill_scaled_rect(ctx, o, s, r, 3, 6, 7, 3);
}

static void prv_segment_lower_left(GContext *ctx, GPoint o, int s, int r) {
  prv_fill_scaled_rect(ctx, o, s, r, 0, 7, 3, 6);
}

static void prv_segment_lower_right(GContext *ctx, GPoint o, int s, int r) {
  prv_fill_scaled_rect(ctx, o, s, r, 10, 7, 3, 6);
}

static void prv_segment_bottom(GContext *ctx, GPoint o, int s, int r) {
  prv_fill_scaled_rect(ctx, o, s, r, 3, 12, 7, 3);
}

static void __attribute__((unused)) prv_draw_segmented_digit(GContext *ctx, char digit,
                                                             GPoint origin, int scale,
                                                             int radius) {
  switch (digit) {
    case '0':
      prv_segment_top(ctx, origin, scale, radius);
      prv_segment_upper_left(ctx, origin, scale, radius);
      prv_segment_upper_right(ctx, origin, scale, radius);
      prv_segment_lower_left(ctx, origin, scale, radius);
      prv_segment_lower_right(ctx, origin, scale, radius);
      prv_segment_bottom(ctx, origin, scale, radius);
      break;
    case '1':
      prv_fill_scaled_rect(ctx, origin, scale, radius, 3, 2, 4, 3);
      prv_fill_scaled_rect(ctx, origin, scale, radius, 6, 0, 4, 13);
      prv_fill_scaled_rect(ctx, origin, scale, radius, 2, 12, 9, 3);
      break;
    case '2':
      prv_segment_top(ctx, origin, scale, radius);
      prv_segment_upper_right(ctx, origin, scale, radius);
      prv_segment_middle(ctx, origin, scale, radius);
      prv_segment_lower_left(ctx, origin, scale, radius);
      prv_segment_bottom(ctx, origin, scale, radius);
      break;
    case '3':
      prv_segment_top(ctx, origin, scale, radius);
      prv_segment_upper_right(ctx, origin, scale, radius);
      prv_segment_middle(ctx, origin, scale, radius);
      prv_segment_lower_right(ctx, origin, scale, radius);
      prv_segment_bottom(ctx, origin, scale, radius);
      break;
    case '4':
      prv_segment_upper_left(ctx, origin, scale, radius);
      prv_segment_upper_right(ctx, origin, scale, radius);
      prv_segment_middle(ctx, origin, scale, radius);
      prv_segment_lower_right(ctx, origin, scale, radius);
      break;
    case '5':
      prv_segment_top(ctx, origin, scale, radius);
      prv_segment_upper_left(ctx, origin, scale, radius);
      prv_segment_middle(ctx, origin, scale, radius);
      prv_segment_lower_right(ctx, origin, scale, radius);
      prv_segment_bottom(ctx, origin, scale, radius);
      break;
    case '6':
      prv_segment_top(ctx, origin, scale, radius);
      prv_segment_upper_left(ctx, origin, scale, radius);
      prv_segment_middle(ctx, origin, scale, radius);
      prv_segment_lower_left(ctx, origin, scale, radius);
      prv_segment_lower_right(ctx, origin, scale, radius);
      prv_segment_bottom(ctx, origin, scale, radius);
      break;
    case '7':
      prv_segment_top(ctx, origin, scale, radius);
      prv_segment_upper_right(ctx, origin, scale, radius);
      prv_segment_lower_right(ctx, origin, scale, radius);
      prv_fill_scaled_rect(ctx, origin, scale, radius, 7, 5, 3, 4);
      break;
    case '8':
      prv_segment_top(ctx, origin, scale, radius);
      prv_segment_upper_left(ctx, origin, scale, radius);
      prv_segment_upper_right(ctx, origin, scale, radius);
      prv_segment_middle(ctx, origin, scale, radius);
      prv_segment_lower_left(ctx, origin, scale, radius);
      prv_segment_lower_right(ctx, origin, scale, radius);
      prv_segment_bottom(ctx, origin, scale, radius);
      break;
    case '9':
      prv_segment_top(ctx, origin, scale, radius);
      prv_segment_upper_left(ctx, origin, scale, radius);
      prv_segment_upper_right(ctx, origin, scale, radius);
      prv_segment_middle(ctx, origin, scale, radius);
      prv_segment_lower_right(ctx, origin, scale, radius);
      prv_segment_bottom(ctx, origin, scale, radius);
      break;
  }
}

static int prv_digit_width_units(char digit) {
#if SQUINTLESS_NUMERAL_STYLE == SQUINTLESS_STYLE_SOLID
  return digit == '1' ? SOLID_ONE_UNITS_W : DIGIT_UNITS_W;
#else
  return DIGIT_UNITS_W;
#endif
}

static int prv_digit_spacing_units(char left, char right,
                                   const SquintlessLayout *layout) {
#if SQUINTLESS_NUMERAL_STYLE == SQUINTLESS_STYLE_SOLID
  if (left == '1' && right == '1') {
    return 3;
  }
  if (left == '1' || right == '1') {
    return 2;
  }
  if ((left == '0' && right == '8') || (left == '8' && right == '8')) {
    return 1;
  }
  return layout->default_digit_spacing_units;
#else
  return layout->default_digit_spacing_units;
#endif
}

static void prv_draw_style_digit(GContext *ctx, char digit, GPoint origin,
                                 int scale, int radius) {
#if SQUINTLESS_NUMERAL_STYLE == SQUINTLESS_STYLE_SOLID
  prv_draw_solid_digit(ctx, digit, origin, scale, radius);
#else
  prv_draw_segmented_digit(ctx, digit, origin, scale, radius);
#endif
}

static int prv_number_width_units(const char *text, int digit_count,
                                  const SquintlessLayout *layout) {
  int total_units_w = 0;
  for (int i = 0; i < digit_count; i++) {
    total_units_w += prv_digit_width_units(text[i]);
    if (i < digit_count - 1) {
      total_units_w += prv_digit_spacing_units(text[i], text[i + 1], layout);
    }
  }
  return total_units_w;
}

static void prv_draw_number(GContext *ctx, const char *text, GRect bounds,
                            const SquintlessLayout *layout) {
  const int digit_count = strlen(text);
  const int total_units_w = prv_number_width_units(text, digit_count, layout);
  const int scale_by_w = bounds.size.w / total_units_w;
  const int scale_by_h = bounds.size.h / DIGIT_UNITS_H;
  const int scale = scale_by_w < scale_by_h ? scale_by_w : scale_by_h;
  const int number_w = total_units_w * scale;
  const int number_h = DIGIT_UNITS_H * scale;
  const int radius = layout->digit_corner_radius * scale;
  GPoint origin = GPoint(bounds.origin.x + ((bounds.size.w - number_w) / 2),
                        bounds.origin.y + ((bounds.size.h - number_h) / 2));

  int digit_x = origin.x;
  for (int i = 0; i < digit_count; i++) {
    prv_draw_style_digit(ctx, text[i], GPoint(digit_x, origin.y), scale, radius);
    digit_x += prv_digit_width_units(text[i]) * scale;
    if (i < digit_count - 1) {
      digit_x += prv_digit_spacing_units(text[i], text[i + 1], layout) * scale;
    }
  }
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

static void prv_face_update_proc(Layer *layer, GContext *ctx) {
  GRect bounds = layer_get_bounds(layer);
  SquintlessLayout layout = prv_layout_for_bounds(bounds);
  char hour_text[4];
  char minute_text[4];

  prv_get_time_text(hour_text, sizeof(hour_text), minute_text, sizeof(minute_text));

  graphics_context_set_fill_color(ctx, GColorWhite);
  graphics_fill_rect(ctx, bounds, 0, GCornersAll);

  graphics_context_set_fill_color(ctx, GColorBlack);
  prv_draw_number(ctx, hour_text, layout.hour_bounds, &layout);

  int fill_w = (layout.battery_bounds.size.w * s_battery_percent) / 100;
  if (s_battery_percent > 0 && fill_w < layout.low_battery_min_w) {
    fill_w = layout.low_battery_min_w;
  }
  graphics_fill_rect(ctx, GRect(layout.battery_bounds.origin.x,
                                layout.battery_bounds.origin.y,
                                fill_w,
                                layout.battery_bounds.size.h),
                     0, GCornersAll);

  prv_draw_number(ctx, minute_text, layout.minute_bounds, &layout);
}

static void prv_tick_handler(struct tm *tick_time, TimeUnits units_changed) {
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
  battery_state_service_subscribe(prv_battery_handler);
  tick_timer_service_subscribe(MINUTE_UNIT, prv_tick_handler);

  window_stack_push(s_window, false);
}

static void prv_deinit(void) {
  tick_timer_service_unsubscribe();
  battery_state_service_unsubscribe();
  window_destroy(s_window);
}

int main(void) {
  prv_init();
  app_event_loop();
  prv_deinit();
}
