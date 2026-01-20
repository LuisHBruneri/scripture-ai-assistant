import 'dart:convert';
import 'dart:math';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

class ApiService {
  // Use localhost for iOS simulator, 10.0.2.2 for Android emulator
  // Or the machine's local IP if testing on real device.
  // If Web (Docker/Nginx), use relative path to let Nginx proxy handle it.
  static String get _baseUrl {
     if (kIsWeb) {
       // On web, empty string means relative to current origin (e.g. http://localhost:3000)
       // But http package needs full URI usually, or we handle it carefully.
       // Actually, passing just '/chat' to Uri.parse might need care.
       // Let's rely on Nginx proxy at root. 
       // If we access http://localhost:3000, we want to hit http://localhost:3000/chat
       // Uri.base.origin gives us the current origin
       // HOWEVER: simpler to just assume if we are in docker, we accessed via port 3000
       return ""; 
     }
     return 'http://localhost:8001';
  }
  
  // Helper to switch base URL if needed (e.g. via settings)
  String baseUrl = _baseUrl;
  
  late final String _sessionId;

  ApiService() {
    _sessionId = _generateSessionId();
    // If web, ensure we don't have double slash issues or empty host
    if (kIsWeb && baseUrl.isEmpty) {
       // baseUrl stays empty, requests become '/chat'
    }
  }

  String _generateSessionId() {
    final random = Random();
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final randomPart = random.nextInt(1000000);
    return 'session_$timestamp$randomPart';
  }

  Stream<Map<String, dynamic>> sendMessageStream(String query) async* {
    final client = http.Client();
    try {
      final request = http.Request('POST', Uri.parse('$baseUrl/chat'));
      request.headers['Content-Type'] = 'application/json';
      request.body = jsonEncode({
        'query': query,
        'session_id': _sessionId,
      });

      final response = await client.send(request);

      if (response.statusCode != 200) {
        throw Exception('Failed to connect: ${response.statusCode}');
      }

      final stream = response.stream
          .transform(utf8.decoder)
          .transform(const LineSplitter());

      await for (final line in stream) {
        if (line.startsWith('data: ')) {
          final jsonStr = line.substring(6);
          try {
            final data = jsonDecode(jsonStr);
            yield data;
          } catch (e) {
            if (kDebugMode) print("Error parsing SSE JSON: $e");
          }
        }
      }
    } catch (e) {
      if (kDebugMode) print("API Stream Error: $e");
      throw e;
    } finally {
      client.close();
    }
  }
}
