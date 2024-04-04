local mon = peripheral.wrap("top")
mon.setTextScale(0.5)
mon.setCursorPos(1, 1)
mon.clear()
os.loadAPI("json")

local emptyText = string.rep(" ", 676)
local defaultColor = string.rep("0", 676)

while true do
	local conn = http.get("http://127.0.0.1:5000/getRS")
	local img = conn.readAll()
	conn.close()
	local outmap = json.decode(img)
	
	for rowIdx = 1, #outmap
	do
		mon.setCursorPos(1, rowIdx)
		mon.blit(emptyText, defaultColor, outmap[rowIdx])
	end
end