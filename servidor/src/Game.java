import java.io.*;
import java.util.concurrent.*;

/**
 * Classe representando um jogo.
 * <p>
 * Gerencia clientes.
 */
public class Game {

	/**
	 * Mapeia cada cliente por um token único.
	 */
	protected ConcurrentHashMap<String, Client> clients =
		new ConcurrentHashMap<String, Client>();

	/**
	 * Cria um novo cliente e o mapeia, se já não existir.
	 *
	 * @param token O token que mapeia o cliente.
	 * @return Se o cliente não existia e foi adicionado com sucesso.
	 */
	public boolean create(String token)
	{
		if (clients.containsKey(token))
			return false;
		clients.put(token, new Client(token));
		return true;
	}

	/**
	 * Remove um cliente e fecha todas suas conexões, se existir.
	 *
	 * @param token O token que mapeia o cliente.
	 * @return Se o cliente existia e foi removido com sucesso.
	 */
	public boolean remove(String token)
	{
		Client c = clients.remove(token);
		if (c == null)
			return false;
		for (OutputStream o : c.streams)
			try {
				o.close();
			} catch (IOException e) {
				e.printStackTrace();
			} finally {
				continue;
			}
		return true;
	}

	/**
	 * Adiciona um canal de escuta para um cliente, se existir.
	 *
	 * @param token O token que mapeia o cliente.
	 * @param stream O canal.
	 * @return Se o cliente existe.
	 */
	public boolean addStream(String token, OutputStream stream)
	{
		Client c = clients.get(token);
		if (c == null)
			return false;
		c.addStream(stream);
		return true;
	}

	/**
	 * Envia uma mensagem para todos os clientes.
	 *
	 * @param data A mensagem.
	 * @see #stream(String)
	 */
	public void broadcast(String data)
	{
		for (Client c : clients.values())
			c.stream(data);
	}

}
