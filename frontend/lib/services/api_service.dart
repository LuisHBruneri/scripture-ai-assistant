import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

class ApiService {
  // Use localhost for iOS simulator, 10.0.2.2 for Android emulator
  // Or the machine's local IP if testing on real device.
  static const String _baseUrl = 'http://localhost:8001'; 
  
  // Helper to switch base URL if needed (e.g. via settings)
  String baseUrl = _baseUrl;

  Future<Map<String, dynamic>> sendMessage(String query) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/chat'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'query': query}),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to load response: ${response.statusCode}');
      }
    } catch (e) {
      if (kDebugMode) {
        print("API Error: $e");
      }
      throw Exception('Failed to connect to server');
    }
  }
}
