import java.io.IOException;
import java.io.OutputStream;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedDeque;

class Client {

	protected static ConcurrentHashMap<Integer, Client> pool;

	protected ConcurrentLinkedDeque<OutputStream> streams;
	protected Integer token;

	static
	{
		pool = new ConcurrentHashMap<Integer, Client>();
	}

	public static void addStream(Integer token, OutputStream stream)
	{
		Client c = pool.get(token);
		if (c != null)
			c.streams.add(stream);
	}

	public static void broadcast(String data)
	{
		for (Client c : pool.values())
			c.stream(data);
	}

	public Client(Integer token)
	{
		this.token = token;
		streams = new ConcurrentLinkedDeque<OutputStream>();

		pool.putIfAbsent(token, this);
	}

	public void stream(String data)
	{
		data += "\n";
		for (OutputStream o : streams) {
			try {
				o.write(data.getBytes());
				o.flush();
			} catch (IOException e1) {
				try {
					o.close();
				} catch (IOException e2) {
					e2.printStackTrace();
				} finally {
					streams.remove(o);
				}
			}
		}
	}

}
