import java.io.IOException;
import java.io.OutputStream;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedDeque;

class Client {

	// todos os clientes, mapeados pelos seus tokens
	protected static ConcurrentHashMap<String, Client> pool =
		new ConcurrentHashMap<String, Client>();

	// um cliente pode escutar mensagens através de mais uma conexão
	protected ConcurrentLinkedDeque<OutputStream> streams =
		new ConcurrentLinkedDeque<OutputStream>();
	// identificador do cliente
	protected final String token;

	// caso não exista um cliente com o token, adiciona um novo ao mapa
	public static void create(String token)
	{
		pool.putIfAbsent(token, new Client(token));
	}

	// caso não exista um cliente com o token, adiciona um novo ao mapa
	public static boolean remove(String token)
	{
		Client c = pool.remove(token);
		if (c == null)
			return false;
		for (OutputStream o : c.streams)
			try {
				o.close();
			} catch (IOException e) {
				e.printStackTrace();
			}
		return true;
	}

	// procura o cliente correspondente a um token e adiciona uma conexão para
	// escuta. retorna false se o cliente não existe.
	public static boolean addStream(String token, OutputStream stream)
	{
		Client c = pool.get(token);
		if (c == null)
			return false;
		c.streams.add(stream);
		return true;
	}

	// envia uma mensagem para todos os clientes
	public static void broadcast(String data)
	{
		for (Client c : pool.values())
			c.stream(data);
	}

	// construtor
	protected Client(String token)
	{
		this.token = token;
	}

	// envia uma mensagem para o cliente através de todas as suas conexões de
	// escuta
	public void stream(String data)
	{
		// faz com que a mensagem inteira possa ser lida com um "readLine()"
		// o cliente deve formatar a mensagem de volta - trivial
		data.replaceAll("\\n", "\\\\n");
		data.replaceAll("\n", "\\n");
		data += "\n";

		for (OutputStream o : streams) {
			try {
				o.write(data.getBytes());
				o.flush();
			} catch (IOException e1) {
				e1.printStackTrace();
				// se a conexão está quebrada, remove da lista
				try {
					// garante o fechamento
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
