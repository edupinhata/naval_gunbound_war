import java.io.*;
import java.util.concurrent.*;

/**
 * Classe representando um único cliente, que pode se comunicar por vários
 * canais.
 * <p>
 * Gerencia suas próprias instâncias através de campos estáticos.
 */
public class Client {

	/**
	 * Mapeia cada cliente por um token único.
	 */
	protected static ConcurrentHashMap<String, Client> pool =
		new ConcurrentHashMap<String, Client>();

	/**
	 * Lista de canais de saída do cliente.
	 */
	protected ConcurrentLinkedDeque<OutputStream> streams =
		new ConcurrentLinkedDeque<OutputStream>();

	/**
	 * Identificador único do cliente.
	 */
	protected final String token;

	/**
	 * Cria um novo cliente e o mapeia, se já não existir.
	 *
	 * @param token O token que mapeia o cliente.
	 * @return Se o cliente não existia e foi adicionado com sucesso.
	 */
	public static boolean create(String token)
	{
		if (pool.containsKey(token))
			return false;
		pool.put(token, new Client(token));
		return true;
	}

	/**
	 * Remove um cliente e fecha todas suas conexões, se existir.
	 *
	 * @param token O token que mapeia o cliente.
	 * @return Se o cliente existia e foi removido com sucesso.
	 */
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
	public static boolean addStream(String token, OutputStream stream)
	{
		Client c = pool.get(token);
		if (c == null)
			return false;
		c.streams.add(stream);
		return true;
	}

	/**
	 * Envia uma mensagem para todos os clientes.
	 *
	 * @param data A mensagem.
	 * @see #stream(String)
	 */
	public static void broadcast(String data)
	{
		for (Client c : pool.values())
			c.stream(data);
	}

	/**
	 * Construtor.
	 *
	 * @see #create(String)
	 */
	protected Client(String token)
	{
		this.token = token;
	}

	/**
	 * Envia uma mensagem para o cliente através de todas os seus canais de
	 * escuta.
	 * <p>
	 * Como o campo Content-Length é omitido, o cliente não sabe o tamanho de
	 * cada mensagem, portanto a mensagem é formatada para que ocupe apenas uma
	 * linha, indicando o fim de uma única mensagem.
	 * <p>
	 * Se algum canal estiver fechado/quebrado, é removido da lista do cliente.
	 *
	 * @param data A mensagem.
	 * @see #streams
	 */
	public void stream(String data)
	{
		data.replaceAll("\\n", "\\\\n");
		data.replaceAll("\n", "\\n");
		data += "\n";

		for (OutputStream o : streams) {
			try {
				o.write(data.getBytes());
				o.flush();
			} catch (IOException e1) {
				e1.printStackTrace();
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
