import java.io.IOException;
import java.io.OutputStream;
import java.math.BigInteger;
import java.security.MessageDigest;
import com.sun.net.httpserver.HttpExchange;

public class Tokenizer extends Handler {

	// o token é gerado a partir do hash do IP+porta
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

	@Override
	public void handlePost(HttpExchange e) throws IOException
	{
		OutputStream o = e.getResponseBody();

		String t = getToken(e);
		Client.create(t);

		// envia token para o remetente
		byte[] b = t.getBytes();
		e.sendResponseHeaders(200, b.length);
		o.write(b);

		// fecha a conexão
		o.close();
	}

}
