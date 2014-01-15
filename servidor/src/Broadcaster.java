import java.io.*;
import com.sun.net.httpserver.*;

/**
 * Handler que envia mensagens para todos os clientes.
 *
 * @see Client
 */
public class Broadcaster extends Handler {

	/**
	 * Construtor.
	 *
	 * @see Handler#Handler(Game)
	 */
	public Broadcaster(Game g)
	{
		super(g);
	}

	/**
	 * Lê os dados de uma requisição POST e os envia para todos os clientes.
	 *
	 * @param e O objeto do qual a mensagem é lida.
	 * @throws IOException Se houver erro na conexão com o remetente ou qualquer
	 * cliente.
	 * @see Client#broadcast(String)
	 */
	@Override
	protected void handlePost(HttpExchange e) throws IOException
	{
		Client.broadcast(getBody(e));

		e.sendResponseHeaders(200, 0);
		e.getResponseBody().close();
	}

}
