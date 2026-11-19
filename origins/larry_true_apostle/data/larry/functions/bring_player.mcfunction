tag @s add larry_guest
function larry:save_return
function larry:arrive
tellraw @s {"text":"A hand of blackstone closes around you. Larry's Apostle has dragged you into the Gilded Expanse.","color":"dark_red","italic":true}
tellraw @s [{"text":"[Leave the realm]","color":"gold","bold":true,"clickEvent":{"action":"run_command","value":"/trigger larry_leave"},"hoverEvent":{"action":"show_text","contents":"Return to where you came from"}},{"text":"  or type /trigger larry_leave at any time","color":"gray"}]
