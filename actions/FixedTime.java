import com.google.gson.JsonObject;
import java.util.Timer;
import java.util.TimerTask;
import java.lang.Integer;

public class FixedTime {
	static JsonObject myresp = null;

	public static JsonObject main(JsonObject args) {
		String timeout = "1";
		if (args.has("timeout"))
			timeout = args.getAsJsonPrimitive("timeout").getAsString();
		String interval = "10";
		if (args.has("interval"))
			interval = args.getAsJsonPrimitive("interval").getAsString();

		Timer timer = new Timer();
		timer.schedule(new TimerTask() {
			@Override
			public void run() {
				myresp = new JsonObject();
				System.out.println("time out!");
				myresp.addProperty("msg", "time out!");
			}
		}, 60000 * Integer.parseInt(timeout));

		while (myresp == null) {
			System.out.println("I’m busy");
			try {
				Thread.sleep(100 * Integer.parseInt(interval));
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
		}
		timer.cancel();

		return myresp;
	}
}
