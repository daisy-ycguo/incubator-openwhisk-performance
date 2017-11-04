import com.google.gson.JsonObject;

public class HelloWorld {
	
	public static JsonObject main(JsonObject args) {
		
		String name = "guest";
		if (args.has("name"))
			name = args.getAsJsonPrimitive("name").getAsString();		
		JsonObject response = new JsonObject();
		response.addProperty("greeting", "Hello " + name + "!");
		return response;
		
	}
}
