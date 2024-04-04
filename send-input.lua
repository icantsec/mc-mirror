os.loadAPI("json")
chat = peripheral.wrap("left")

while true do
	event, player, message = os.pullEvent("chat")
	if player ~= nil and player == "iClutchUrPearls" then
		chat.sendMessage("sending " .. message)
		message = message:gsub(" ", "%20")
		conn = http.get("http://127.0.0.1:5000/post?query=" .. message)
		res = conn.readAll()
		conn.close()
		resp = json.decode(res)
		chat.sendMessage("Server response: " .. resp)
	end
end