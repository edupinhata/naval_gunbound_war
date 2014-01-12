import java.io.IOException;
import java.io.OutputStream;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedDeque;

class Client {

	// todos os clientes, mapeados pelos seus tokens
	protected static ConcurrentHashMap<Integer, Client> pool =
		new ConcurrentHashMap<Integer, Client>();

	// um cliente pode escutar mensagens através de mais uma conexão
	protected ConcurrentLinkedDeque<OutputStream> streams =
		new ConcurrentLinkedDeque<OutputStream>();
	// identificador do cliente
	protected final Integer token;

	// procura o cliente correspondente a um token e adiciona uma conexão para
	// escuta
	// TODO retornar true ou false
	public static void addStream(Integer token, OutputStream stream)
	{
		Client c = pool.get(token);
		if (c != null)
			c.streams.add(stream);
	}

	// envia uma mensagem para todos os clientes
	public static void broadcast(String data)
	{
		for (Client c : pool.values())
			c.stream(data);
	}

	// construtor, adiciona ao mapa de todos os clientes se já não existir. se
	// já existir, este objeto será garbage collected.
	// TODO: fazer método estático para criação ao invés disto
	public Client(Integer token)
	{
		this.token = token;

		pool.putIfAbsent(token, this);
	}

	// envia uma mensagem para o cliente através de todos o seus canais de escuta
	public void stream(String data)
	{
		data += "\n";
		for (OutputStream o : streams) {
			try {
				o.write(data.getBytes());
				o.flush();
			} catch (IOException e1) {
				e1.printStackTrace();
				// se o canal está quebrado, remove da lista
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
