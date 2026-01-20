use eframe::egui;

struct MainWindow {
    // Store the last calculated font size to avoid recalculating unnecessarily
    last_font_size: f32,
}

impl Default for MainWindow {
    fn default() -> Self {
        Self {
            last_font_size: 0.0,
        }
    }
}

impl eframe::App for MainWindow {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        // Get the available area size
        let available_size = ctx.available_rect().size();
        let window_width = available_size.x;
        let window_height = available_size.y;

        // Calculate appropriate font size based on window dimensions
        // Base font size calculation (matching Python logic)
        let base_size = (window_width / 20.0).min(window_height / 8.0);
        let base_size = base_size.max(12.0); // Minimum font size

        // Only update if the size has changed significantly (debouncing effect)
        if (base_size - self.last_font_size).abs() > 1.0 {
            self.last_font_size = base_size;
        }

        // Create centered label with auto-resizing text
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.vertical_centered(|ui| {
                ui.add_space(ui.available_height() / 2.0 - base_size);
                
                // Create text with calculated font size
                let text_style = egui::TextStyle::Heading;
                let font_id = egui::FontId {
                    size: self.last_font_size,
                    family: egui::FontFamily::Proportional,
                };
                
                ui.label(
                    egui::RichText::new("Welcome to SEPTAwatch!")
                        .font(font_id)
                        .strong(),
                );
            });
        });
    }
}

fn main() -> Result<(), eframe::Error> {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([500.0, 400.0])
            .with_position([100.0, 100.0]),
        ..Default::default()
    };

    eframe::run_native(
        "SEPTAwatch",
        options,
        Box::new(|_cc| Box::new(MainWindow::default())),
    )
}
