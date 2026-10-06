// SPDX-License-Identifier: Apache-2.0
// Independent offline candidate-vector consumer; not a runtime package.
using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;

var vectors = JsonDocument.Parse(File.ReadAllBytes(args.Single()));
var utf8 = new UTF8Encoding(false, true);
var passed = 0;
foreach (var test in vectors.RootElement.GetProperty("cases").EnumerateArray())
{
    var input = test.GetProperty("input").GetString()!;
    var reject = test.GetProperty("result").GetString() == "reject";
    string? output = null;
    try
    {
        if (utf8.GetByteCount(input) > 65536 || input.StartsWith('\ufeff'))
            throw new FormatException("size or BOM");
        using var document = JsonDocument.Parse(input, new JsonDocumentOptions { MaxDepth = 16 });
        if (document.RootElement.ValueKind != JsonValueKind.Object)
            throw new FormatException("object required");
        output = Canonical(document.RootElement);
        _ = utf8.GetBytes(output);
    }
    catch (Exception error) when (error is JsonException or FormatException
        or InvalidOperationException or EncoderFallbackException)
    {
        if (!reject) throw;
    }
    if (reject != (output is null))
        throw new Exception($"Wrong acceptance: {test.GetProperty("id")}");
    if (!reject)
    {
        var digest = "sha256:" + Convert.ToHexString(SHA256.HashData(
            utf8.GetBytes("munarium:decision-request:v1\0" + output))).ToLowerInvariant();
        if (output != test.GetProperty("canonical").GetString()
            || digest != test.GetProperty("digest").GetString())
            throw new Exception($"Vector mismatch: {test.GetProperty("id")}");
    }
    passed++;
}
Console.WriteLine($"{passed} canonical vectors passed; no runtime or identity qualification");

static string Canonical(JsonElement element)
{
    switch (element.ValueKind)
    {
        case JsonValueKind.Object:
            var fields = new SortedDictionary<string, string>(StringComparer.Ordinal);
            foreach (var field in element.EnumerateObject())
            {
                if (field.Name.Any(c => c > 127) || !fields.TryAdd(field.Name, Canonical(field.Value)))
                    throw new FormatException("member ambiguity");
            }
            return "{" + string.Join(",", fields.Select(f => Quote(f.Key) + ":" + f.Value)) + "}";
        case JsonValueKind.Array:
            return "[" + string.Join(",", element.EnumerateArray().Select(Canonical)) + "]";
        case JsonValueKind.String: return Quote(element.GetString()!);
        case JsonValueKind.Number:
            var token = element.GetRawText();
            if (!Regex.IsMatch(token, @"\A-?(0|[1-9][0-9]*)\z") || token == "-0"
                || !long.TryParse(token, NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out var number)
                || number < -9007199254740991L || number > 9007199254740991L)
                throw new FormatException("number outside profile");
            return token;
        case JsonValueKind.True: return "true";
        case JsonValueKind.False: return "false";
        case JsonValueKind.Null: return "null";
        default: throw new FormatException("unsupported value");
    }
}

static string Quote(string value)
{
    var result = new StringBuilder("\"");
    foreach (var c in value)
        result.Append(c switch
        {
            '"' => "\\\"", '\\' => "\\\\", '\b' => "\\b", '\t' => "\\t",
            '\n' => "\\n", '\f' => "\\f", '\r' => "\\r",
            < ' ' => "\\u" + ((int)c).ToString("x4", CultureInfo.InvariantCulture),
            _ => c.ToString()
        });
    return result.Append('"').ToString();
}
