# Auto Ui
A Home Assistant component to show  each user's most used actions by time of day and week. Maybe you turn off a lamp on Sunday afternoons, maybe you fiddle with the thermostat regularly on Monday mornings. This component stores and outputs this data so it can be used in a Lovelace Card that updates to show your most frequently used entities at the top.

## Using output to drive lovelace card
Outputs are defined in `auto_ui` states, each of which contain an entity_id.

ex: `auto_ui.joel_1 = light.bedroom_lamp`

These outputs will need to be used in a Lovelace card that supports templates in the entity fields. There's a few projects that allow this, in my setup I've used [@iantrich's config-template-card](https://github.com/iantrich/config-template-card) which has worked well. 

Example config using config-template-card:
```type: custom:config-template-card
variables:
  - states['auto_ui.joel_0'].state
  - states['auto_ui.joel_1'].state
  - states['auto_ui.joel_2'].state
  - states['auto_ui.joel_3'].state
  - states['auto_ui.joel_4'].state
  - states['auto_ui.joel_5'].state
  - states['auto_ui.joel_6'].state
  - states['auto_ui.joel_7'].state
  - states['auto_ui.joel_8'].state
  - states['auto_ui.joel_9'].state
entities:
  - ${vars[0]}
card:
  type: entity-filter
  card:
    title: Auto Ui Joel
    show_header_toggle: false
  state_filter:
    - operator: '!='
      value: Placeholder, as the db fills you'll see this less
  entities:
    - ${vars[0]}
    - ${vars[1]}
    - ${vars[2]}
    - ${vars[3]}
    - ${vars[4]}
    - ${vars[5]}
    - ${vars[6]}
    - ${vars[7]}
    - ${vars[8]}
    - ${vars[9]} 
```

## Configuration
Config entry in Home Assistant config. `users` is required and should be formatted as `[haUserId]: [friendly name for the user]`
| Key              | Required | Default | Description                                                     |
|------------------|----------|---------|-----------------------------------------------------------------|
| users            | yes      | []      | List of users to store actions and create output components for |
| card_count       | no       | 10      | Number of cards to output                                       |
| time_block_min   | no       | 120     | Time window size in minutes to match events to.                 |
| entity_blacklist | no       | []      | Array of entity_ids to exclude from output                      |

### Examples
#### Minimal config:

```
auto_ui:
  users:
    aecaac0f0f374df0be98f4918da681c1: joel
```

#### Full config
```
auto_ui:
  users:
    aecaac0f0f374df0be98f4918da681c1: joel
  card_count: 10
  time_block_min: 120
  entity_blacklist:
    - light.ignored_light
    - switch.ignored_switch
```