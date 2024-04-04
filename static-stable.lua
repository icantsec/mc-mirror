local mon = peripheral.wrap("top")
mon.setTextScale(0.5)
mon.setCursorPos(1, 1)
mon.clear()
os.loadAPI("json")

while true do
	conn = http.get("http://127.0.0.1:5000/getRS")
	img = conn.readAll()
	conn.close()
	outmap = json.decode(img)

	for rowIdx = 1, #outmap
	do
		lastX = 0
		for col=1, #outmap[rowIdx]
		do
			currColor = outmap[rowIdx][col][1]
			for currOffset=1,outmap[rowIdx][col][2]
			do
				mon.setCursorPos(lastX+currOffset, rowIdx)
				mon.setBackgroundColor(currColor)
				mon.write(" ")
			end
			lastX = lastX + outmap[rowIdx][col][2]
		end
	end
end