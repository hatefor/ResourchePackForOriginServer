tellraw @s [{"text": "\n✦ ", "color": "gold"}, {"text": "The light stirs. You have met every trial.", "color": "yellow", "bold": true}]
tellraw @s [{"text": "  Stay here and ", "color": "gray"}, {"text": "[ ASCEND ]", "color": "yellow", "bold": true, "clickEvent": {"action": "run_command", "value": "/trigger evo"}, "hoverEvent": {"action": "show_text", "contents": {"text": "Click (or type /trigger evo) to become a Being of Light", "color": "gold"}}}, {"text": " or type /trigger evo", "color": "gray"}]
playsound minecraft:block.beacon.activate player @s ~ ~ ~ 1 1.6
