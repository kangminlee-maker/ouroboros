use slt::{Border, Context, KeyCode};

use crate::state::*;

/// Returns Some(selected_index) when Enter is pressed, None otherwise.
pub fn render(ui: &mut Context, state: &mut AppState) -> Option<usize> {
    let dim = ui.theme().text_dim;
    let surface = ui.theme().surface;
    let surface_hover = ui.theme().surface_hover;
    let text = ui.theme().text;
    let secondary = ui.theme().secondary;
    let accent = ui.theme().accent;

    // Esc returns to previous screen
    if ui.key_code(KeyCode::Esc) {
        state.screen = Screen::Dashboard;
        state.tabs.selected = 0;
    }

    let mut selected = None;

    // Enter selects session
    if ui.key_code(KeyCode::Enter) && !state.sessions.is_empty() {
        selected = Some(state.session_list.selected);
    }

    ui.container().grow(1).gap(1).col(|ui| {
        ui.container().bg(surface_hover).px(3).py(1).col(|ui| {
            ui.text("Session Selector").fg(text).bold();
            ui.row(|ui| {
                ui.text("Select a session to monitor. ").fg(dim);
                ui.text("Enter").fg(accent);
                ui.text(" select  ").fg(dim);
                ui.text("Esc").fg(accent);
                ui.text(" back").fg(dim);
            });
        });

        ui.container()
            .grow(1)
            .border(Border::Single)
            .bg(surface)
            .col(|ui| {
                if state.sessions.is_empty() {
                    ui.container().grow(1).center().col(|ui| {
                        ui.text("No sessions found").fg(dim);
                        ui.text("Run ouroboros workflows to create sessions")
                            .fg(dim);
                        ui.text("or use --mock for demo data").fg(dim);
                    });
                } else {
                    ui.container().grow(1).p(1).col(|ui| {
                        ui.list(&mut state.session_list);
                    });
                }
            });

        if !state.sessions.is_empty() {
            let sel = state.session_list.selected;
            if let Some(session) = state.sessions.get(sel) {
                ui.container().bg(surface_hover).px(3).py(0).row(|ui| {
                    ui.text("Type ").fg(dim);
                    ui.text(&session.aggregate_type).fg(secondary);
                    ui.text("    ID ").fg(dim);
                    ui.text(&session.aggregate_id).fg(accent);
                    ui.text(format!("    {} events", session.event_count))
                        .fg(dim);
                    ui.text(format!("    since {}", session.first_ts)).fg(dim);
                });
            }
        }
    });

    selected
}
