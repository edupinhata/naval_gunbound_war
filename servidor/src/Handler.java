import java.io.*;
import java.util.*;
import com.sun.net.httpserver.*;

/**
 * Um objeto da classe HttpServer construído com um objeto desta classe chama o
 * método handle para o tratamento da requisição HTTP.
 * <p>
 * Esta classe detecta o método da requisição (GET ou POST) e a direciona para o
 * tratamento adequado. Também contém métodos úteis para a extração de
 * informações contidas nas requisições.
 *
 * @see HttpServer
 * @see HttpHandler
 * @see HttpExchange
 * @see #handle(HttpExchange)
 */
public abstract class Handler implements HttpHandler {

	/**
	 * Lê o campo "Content-Length" do cabeçalho de uma requisição HTTP e devolve
	 * seu valor.
	 *
	 * @param e O objeto do qual será extraído o tamanho.
	 * @return O tamanho do corpo da requisição, ou 0 em caso de falha.
	 */
	protected static int getLength(HttpExchange e)
	{
		try {
			return Integer.parseInt(
					e.getRequestHeaders().get("Content-Length").get(0));
		} catch (Exception ex) {
			return 0;
		}
	}

	/**
	 * Lê o corpo da mensagem de uma requisição HTTP e devolve seu conteúdo em
	 * uma String.
	 * <p>
	 * O número de bytes lidos é igual ao que o método getLength retornar sobre
	 * o objeto passado como parâmetro.
	 *
	 * @param e O objeto do qual será lida a mensagem.
	 * @return O conteúdo da mensagem, ou string vazia em caso de falha.
	 * @see #getLength(HttpExchange)
	 */
	protected static String getBody(HttpExchange e)
	{
		try {
			byte[] in = new byte[getLength(e)];
			e.getRequestBody().read(in, 0, in.length);
			return new String(in);
		} catch (Exception ex) {
			return new String();
		}
	}

	/**
	 * Lê os parâmetros da URI de uma requisição HTTP e devolve um objeto Map
	 * que os representem.
	 * <p>
	 * Um parâmetro e seu valor são separados por '=', múltiplos valores são
	 * separados por ',' e múltiplos argumentos são separados por '&amp;'. Por
	 * exemplo, para a URI http://localhost:8000/resource?arg1=x&amp;arg2=1,2 os
	 * parâmetros são arg1 e arg2 e seus valores são, respectivamente, 'x' e
	 * '[1, 2]'.
	 *
	 * @param e O objeto do qual serão lidos os parâmetros.
	 * @return Um objeto que mapeia, para cada parâmetro, uma lista de
	 * valores.
	 */
	protected static Map<String, String[]> getParams(HttpExchange e)
	{
		Map<String, String[]> params =
			new LinkedHashMap<String, String[]>();

		String[] pairs = e.getRequestURI().getQuery().split("&");

		for (String s : pairs) {
			String[] pair = s.split("=");
			params.put(pair[0], pair[1].split(","));
		}

		return params;
	}

	/**
	 * Redireciona o tratamento de uma requisição HTTP para o método adequado.
	 * <p>
	 * Caso o método HTTP utilizado seja GET, chama o método handleGet, caso
	 * POST, handlePost. Se não for nenhum dos dois, chama o método
	 * sendUnavaliable.
	 *
	 * @param e O objeto representando a requisição.
	 * @throws IOException Em caso de erro com a requisição durante o
	 * tratamento.
	 * @see #handleGet(HttpExchange)
	 * @see #handlePost(HttpExchange)
	 * @see #sendUnavaliable(HttpExchange)
	 */
	@Override
	public void handle(HttpExchange e) throws IOException
	{
		String method = e.getRequestMethod();
		if (method.equalsIgnoreCase("GET")) {
			handleGet(e);
		} else if (method.equalsIgnoreCase("POST")) {
			handlePost(e);
		} else {
			sendUnavaliable(e);
		}
	}

	/**
	 * Envia no cabeçalho de resposta à uma requisição HTTP o código 405
	 * indicando método HTTP indisponível/não-implementado, e fecha a conexão.
	 *
	 * @param e O objeto representando a requisição.
	 * @throws IOException Em caso de erro na conexão.
	 */
	private void sendUnavaliable(HttpExchange e) throws IOException
	{
		e.sendResponseHeaders(405, 0);
		e.getResponseBody().close();
	}

	/**
	 * Método para tratar uma requisição usando o método GET.
	 * <p>
	 * Apenas chama o método sendUnavaliable. É esperado que subclasses
	 * re-implementem este método.
	 *
	 * @param e O objeto representando a requisição.
	 * @throws IOException Em caso de erro na conexão.
	 * @see #sendUnavaliable(HttpExchange)
	 */
	protected void handleGet(HttpExchange e) throws IOException
	{
		sendUnavaliable(e);
	}

	/**
	 * Método para tratar uma requisição usando o método POST.
	 * <p>
	 * Apenas chama o método sendUnavaliable. É esperado que subclasses
	 * re-implementem este método.
	 *
	 * @param e O objeto representando a requisição.
	 * @throws IOException Em caso de erro na conexão.
	 * @see #sendUnavaliable(HttpExchange)
	 */
	protected void handlePost(HttpExchange e) throws IOException
	{
		sendUnavaliable(e);
	}

}
