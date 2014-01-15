import java.io.*;
import com.sun.net.httpserver.*;

/**
 * Handler que remove um cliente.
 *
 * @see Client
 */
public class Deleter extends Handler {

	/**
	 * Construtor.
	 *
	 * @see Handler#Handler(Game)
	 */
	public Deleter(Game g)
	{
		super(g);
	}

	/**
	 * Lê um token do corpo da requisição POST e remove o cliente
	 * correspondente.
	 * <p>
	 * Se o cliente não existir, retorna código de erro 404 Not Found.
	 * <p>
	 *
	 * @param e O objeto que representa a requisição.
	 * @throws IOException Se houver erro na conexão.
	 * @see Client#remove(String)
	 */
	@Override
	public void handlePost(HttpExchange e) throws IOException
	{
		if (!Client.remove(getBody(e)))
			e.sendResponseHeaders(404, 0);
		else
			e.sendResponseHeaders(200, 0);

		e.getResponseBody().close();
	}

}
