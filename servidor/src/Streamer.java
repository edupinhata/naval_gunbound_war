import java.io.*;
import java.util.*;
import com.sun.net.httpserver.*;

/**
 * Handler que adiciona um canal de escuta a um cliente.
 *
 * @see Client
 */
public class Streamer extends Handler {

	/**
	 * Construtor.
	 *
	 * @see Handler#Handler(Game)
	 */
	public Streamer(Game g)
	{
		super(g);
	}

	/**
	 * A partir de um token, mantém a conexão de saída da requisição GET aberta
	 * para que todas as mensagens enviadas para o respectivo cliente sejam
	 * enviadas para esta conexão.
	 * <p>
	 * O token do cliente deve ser passado por parâmetro na query da URI.
	 * Exemplo: ?token=0123456789abcdef. Se não for passado, retorna o código de
	 * erro 400 Bad Request, e se o cliente não existir, retorna o código de
	 * erro 404 Not Found. Nestes casos, a conexão é fechada.
	 *
	 * @param e O objeto representando a requisição.
	 * @throws IOException Se houver erro na conexão.
	 * @see Client#stream(String)
	 */
	@Override
	public void handleGet(HttpExchange e) throws IOException
	{
		OutputStream o = e.getResponseBody();

		Map<String, String[]> p = getParams(e);
		String[] t = p.get("token");
		if (t == null) {
			e.sendResponseHeaders(400, 0);
			o.close();
			return;
		}

		if (!game.addStream(t[0], o)) {
			e.sendResponseHeaders(404, 0);
			o.close();
			return;
		}

		e.sendResponseHeaders(200, 0);
	}

}
