import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:theological_agent/screens/chat_screen.dart'; // Correct package name from pubspec
// Note: We might need to handle dependency injection or mock ApiService if we test logic,
// but for a smoke test of the UI rendering, we can start simple.
// Since ChatScreen instantiates ApiService internally, testing the button tap will invoke HTTP.
// For a safe UI test, we should verify the initial state.

void main() {
  testWidgets('ChatScreen loads and displays input field', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MaterialApp(home: ChatScreen()));

    // Verify that the title is displayed.
    expect(find.text('Agente Teológico'), findsOneWidget);

    // Verify input field exists.
    expect(find.byType(TextField), findsOneWidget);

    // Verify send button exists.
    expect(find.byIcon(Icons.send), findsOneWidget);
  });
}
