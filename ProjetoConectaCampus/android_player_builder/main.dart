import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:webview_flutter/webview_flutter.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  SystemChrome.setPreferredOrientations([
    DeviceOrientation.landscapeLeft,
    DeviceOrientation.landscapeRight,
  ]);

  SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);

  runApp(const ConectaCampusApp());
}

class ConectaCampusApp extends StatelessWidget {
  const ConectaCampusApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      title: 'Conecta Campus',
      debugShowCheckedModeBanner: false,
      home: PlayerScreen(),
    );
  }
}

class PlayerScreen extends StatefulWidget {
  const PlayerScreen({super.key});

  @override
  State<PlayerScreen> createState() => _PlayerScreenState();
}

class _PlayerScreenState extends State<PlayerScreen> with WidgetsBindingObserver {
  late final WebViewController controller;
  Timer? reloadTimer;

  // IMPORTANTE:
  // No Android/TV Box, localhost aponta para o próprio aparelho, não para o PC.
  // Use o IP do computador/servidor na mesma rede.
  static const String url = 'http://192.168.15.39:5000/player/clovis_moura';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);

    controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(Colors.black)
      ..setNavigationDelegate(
        NavigationDelegate(
          onWebResourceError: (error) {
            Future.delayed(const Duration(seconds: 10), () {
              if (mounted) controller.loadRequest(Uri.parse(url));
            });
          },
        ),
      )
      ..loadRequest(Uri.parse(url));

    reloadTimer = Timer.periodic(const Duration(minutes: 10), (_) {
      SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);
      controller.reload();
    });
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);
      controller.reload();
    }
  }

  @override
  void dispose() {
    reloadTimer?.cancel();
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: false,
      child: Scaffold(
        backgroundColor: Colors.black,
        body: WebViewWidget(controller: controller),
      ),
    );
  }
}
