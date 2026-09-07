import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/app.dart';

void main() {
  testWidgets('Travel Copilot App initializes and renders correctly', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: TravelCopilotApp(),
      ),
    );

    // Pump frames through splash delay
    await tester.pump(const Duration(milliseconds: 200));
    await tester.pump(const Duration(seconds: 2));

    expect(find.byType(TravelCopilotApp), findsOneWidget);
  });
}
