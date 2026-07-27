import edu.illinois.cs.cogcomp.quant.driver.Quantifier;
import edu.illinois.cs.cogcomp.quant.driver.QuantSpan;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;

/**
 * Roda o Illinois Quantifier (CogComp) sobre um arquivo de texto (uma sentenca
 * por linha) via getSpans(text, true, null), evitando o trainOnAll() do main().
 * Usa o construtor eager (false) para carregar o classificador.
 *
 * Saida (uma sentenca por bloco), parseavel pelo adapter Python:
 *   ===LINE===\n<texto>\n   seguido de 0+ linhas:
 *   SPAN\t<start>\t<end>\t<classe>\t<object.toString()>
 */
public class RunIllQ {
    public static void main(String[] args) throws Exception {
        Quantifier q = new Quantifier(false);
        for (String line : Files.readAllLines(Paths.get(args[0]))) {
            if (line.trim().isEmpty()) continue;
            System.out.println("===LINE===");
            System.out.println(line);
            try {
                List<QuantSpan> spans = q.getSpans(line, true, null);
                if (spans != null) {
                    for (QuantSpan qs : spans) {
                        if (qs == null || qs.object == null) continue;
                        String obj = String.valueOf(qs.object).replace("\t", " ").replace("\n", " ");
                        System.out.println("SPAN\t" + qs.start + "\t" + qs.end + "\t"
                                + qs.object.getClass().getSimpleName() + "\t" + obj);
                    }
                }
            } catch (Throwable t) {
                System.out.println("ERR\t" + t.getClass().getSimpleName() + "\t" + t.getMessage());
            }
        }
        System.out.println("===END===");
    }
}
