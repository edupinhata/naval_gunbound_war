import java.io.IOException;
import java.io.InputStream;
import com.sun.net.httpserver.HttpExchange;

public class Broadcaster extends Handler {

	@Override
	protected void handlePost(HttpExchange e) throws IOException
	{
		// lê o tamanho da mensagem
		String h = e.getRequestHeaders().get("Content-Length").get(0);
		int length = Integer.parseInt(h);

		// lê a mensagem no buffer
		byte[] data = new byte[length];
		e.getRequestBody().read(data);

		// envia a mensagem para todos os clientes
		Client.broadcast(new String(data));

		// retorna ok para o remetente
		e.sendResponseHeaders(200, 0); // OK
		e.getResponseBody().close();
	}

}
