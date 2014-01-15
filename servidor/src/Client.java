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
	 * Lista de canais de saída do cliente.
	 */
	protected ConcurrentLinkedDeque<OutputStream> streams =
		new ConcurrentLinkedDeque<OutputStream>();

	/**
	 * Identificador único do cliente.
	 */
	protected final String token;

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
