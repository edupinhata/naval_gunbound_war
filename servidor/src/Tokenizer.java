import java.io.IOException;
import java.io.OutputStream;
import java.math.BigInteger;
import java.security.MessageDigest;
import com.sun.net.httpserver.HttpExchange;

/**
 * Handler que cria um cliente e o mapeia para um token.
 *
 * @see Client
 */
public class Tokenizer extends Handler {

	/**
	 * Gera um token a partir do hash do endereço do remetente.
	 *
	 * @param e O objeto do qual o endereço é lido.
	 * @return O token.
	 */
	protected static String getToken(HttpExchange e)
	{
		String t = "";
		try {
			MessageDigest d = MessageDigest.getInstance("MD5");
			byte[] in = e.getRemoteAddress().toString().getBytes();
			byte[] out = d.digest(in);
			t = new BigInteger(1, out).toString(16);
		} catch (Exception ex) {
			ex.printStackTrace();
		} finally {
			return t;
		}
	}

	/**
	 * Cria um cliente e devolve seu token para o remetente da requisição POST.
	 * <p>
	 * O código 201 Created é retornado no cabeçalho.
	 *
	 * @param e O objeto que representa a requisição.
	 * @throws IOException Se houver erro na conexão.
	 * @see Client#create(String)
	 */
	@Override
	public void handlePost(HttpExchange e) throws IOException
	{
		OutputStream o = e.getResponseBody();

		String t = getToken(e);
		byte[] b = t.getBytes();

		if (!Client.create(t));
			e.sendResponseHeaders(200, b.length);
		else
			e.sendResponseHeaders(201, b.length);

		o.write(b);
		o.close();
	}

}
