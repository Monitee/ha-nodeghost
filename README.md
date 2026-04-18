# NodeGhost for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Private AI memory and inference for Home Assistant, powered by [NodeGhost](https://nodeghost.ai) and the POKT decentralized network.

## What it does

NodeGhost gives your Home Assistant AI a persistent, private memory. Store context about your home, routines, and preferences — the AI remembers them across conversations.

- **Private by design** — your data routes through the POKT decentralized network, not Big Tech servers
- **Persistent memory** — store and recall facts about your home automatically via automations
- **OpenAI compatible** — works with the existing HA OpenAI integration, just point it at NodeGhost

## Installation

### HACS (recommended)
1. Add this repo as a custom repository in HACS
2. Search for "NodeGhost" and install
3. Restart Home Assistant

### Manual
1. Copy `custom_components/nodeghost` to your HA `custom_components` folder
2. Restart Home Assistant

## Setup

1. Go to Settings → Integrations → Add Integration
2. Search for "NodeGhost"
3. Enter your NodeGhost API key (get one at [nodeghost.ai](https://nodeghost.ai))
4. Click Submit

## Services

### `nodeghost.remember`
Store a memory for future AI context.

```yaml
service: nodeghost.remember
data:
  text: "Living room lights turned on at 9pm"
  namespace: default
```

### `nodeghost.recall`
Recall relevant memories based on a query. Fires a `nodeghost_recall_result` event with the results.

```yaml
service: nodeghost.recall
data:
  query: "what time do the lights usually turn on"
  namespace: default
```

## Example Automations

### Store context when someone arrives home
```yaml
automation:
  - alias: "NodeGhost — Log arrival"
    trigger:
      - platform: state
        entity_id: person.jaren
        to: home
    action:
      - service: nodeghost.remember
        data:
          text: "{{ person_name }} arrived home at {{ now().strftime('%I:%M %p') }}"
```

### Store context when a scene is activated
```yaml
automation:
  - alias: "NodeGhost — Log movie mode"
    trigger:
      - platform: state
        entity_id: scene.movie_mode
        to: active
    action:
      - service: nodeghost.remember
        data:
          text: "Movie mode activated at {{ now().strftime('%I:%M %p on %A') }}"
```

### Store daily home summary
```yaml
automation:
  - alias: "NodeGhost — Nightly summary"
    trigger:
      - platform: time
        at: "23:00:00"
    action:
      - service: nodeghost.remember
        data:
          text: >
            Nightly summary {{ now().strftime('%A %B %d') }}:
            All lights off: {{ is_state('group.all_lights', 'off') }}.
            Front door locked: {{ is_state('lock.front_door', 'locked') }}.
            Temperature: {{ states('sensor.thermostat_temperature') }}°F.
```

## Using with Home Assistant AI

Point the HA OpenAI integration at NodeGhost:

- **Base URL:** `https://nodeghost.ai/v1`
- **API Key:** your ng- key
- **Model:** your registered model (e.g. `deepseek-chat`)

NodeGhost will automatically inject stored memories as context into every AI conversation.

## Privacy

All memory data routes through the POKT decentralized network. NodeGhost never sees your plaintext memories when encryption is enabled. Your ng- key is stored locally in Home Assistant and never shared.

## Links

- [NodeGhost](https://nodeghost.ai)
- [POKT Network](https://pokt.network)
- [Report Issues](https://github.com/Monitee/ha-nodeghost/issues)
