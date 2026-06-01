import type { Event } from "./types";

export interface Preset {
  label: string;
  description: string;
  timeline: Event[];
}

export const PRESETS: Preset[] = [
  {
    label: "Long COVID pattern",
    description: "Post-exertional crashes, brain fog, unrefreshing sleep",
    timeline: [
      { day: 1, type: "symptom", text: "brain fog · heavy", severity: 4 },
      { day: 2, type: "symptom", text: "unrefreshing sleep again", severity: 3 },
      { day: 3, type: "symptom", text: "crashed after morning walk", severity: 5 },
      { day: 4, type: "symptom", text: "PEM hitting — back to bed", severity: 5 },
      { day: 5, type: "symptom", text: "HR spike just standing up", severity: 3 },
      { day: 6, type: "symptom", text: "taste still off", severity: 2 },
      { day: 7, type: "symptom", text: "finally a 5/10 day", severity: 2 },
    ],
  },
  {
    label: "POTS-like pattern",
    description: "Orthostatic symptoms — dizziness, racing heart on standing",
    timeline: [
      { day: 1, type: "symptom", text: "heart racing 118bpm just standing up", severity: 4 },
      { day: 2, type: "symptom", text: "dizzy getting out of bed", severity: 4 },
      { day: 3, type: "symptom", text: "pre-syncope in the shower", severity: 5 },
      { day: 4, type: "symptom", text: "fatigue · can't do stairs", severity: 4 },
      { day: 5, type: "symptom", text: "nausea all morning", severity: 3 },
      { day: 6, type: "symptom", text: "better lying down", severity: 2 },
      { day: 7, type: "symptom", text: "palpitations after lunch", severity: 3 },
    ],
  },
  {
    label: "GI / gut pattern",
    description: "Bloating, cramping, food reactions after meals",
    timeline: [
      { day: 1, type: "symptom", text: "bloated again 😩", severity: 4 },
      { day: 2, type: "symptom", text: "cramps after lunch · bad", severity: 4 },
      { day: 3, type: "symptom", text: "GI flare, skipped dinner", severity: 5 },
      { day: 4, type: "symptom", text: "loose stool · 3x", severity: 3 },
      { day: 5, type: "symptom", text: "nausea in the morning", severity: 3 },
      { day: 6, type: "symptom", text: "reaction after fermented food", severity: 4 },
      { day: 7, type: "symptom", text: "gas pain · uncomfortable all day", severity: 3 },
    ],
  },
];
