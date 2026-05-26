import 'dart:async';
import 'dart:io';

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

enum PlayerStatus { searching, online, offline }

class PlayerScreen extends StatefulWidget {
  const PlayerScreen({super.key});

  @override
  State<PlayerScreen> createState() => _PlayerScreenState();
}

class _PlayerScreenState extends State<PlayerScreen> with WidgetsBindingObserver {
  late final WebViewController controller;
  Timer? retryTimer;
  Timer? keepAliveTimer;

  PlayerStatus status = PlayerStatus.searching;
  String? serverBaseUrl;
  String? playerUrl;
  String message = 'Procurando servidor Conecta Campus na rede...';

  static const String playerPath = '/player/clovis_moura';
  static const int serverPort = 5000;

  // IPs conhecidos/frequentes. O app testa estes primeiro e depois varre a rede.
  static const List<String> preferredHosts = [
    '192.168.15.39',
    '192.168.0.50',
    '192.168.0.39',
    '192.168.1.50',
    '192.168.1.39',
    '10.0.0.50',
  ];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);

    controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(Colors.black)
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageFinished: (_) {
            if (mounted) setState(() => status = PlayerStatus.online);
          },
          onWebResourceError: (_) {
            _markOfflineAndRetry('Servidor caiu ou a TV Box perdeu conexão. Tentando reconectar...');
          },
        ),
      );

    _startDiscovery();
    keepAliveTimer = Timer.periodic(const Duration(minutes: 5), (_) async {
      await _healthCheckOrReconnect();
    });
  }

  Future<void> _startDiscovery() async {
    retryTimer?.cancel();
    if (mounted) {
      setState(() {
        status = PlayerStatus.searching;
        message = 'Procurando servidor Conecta Campus na rede...';
      });
    }

    final found = await _findServer();
    if (!mounted) return;

    if (found != null) {
      serverBaseUrl = found;
      playerUrl = '$found$playerPath';
      setState(() {
        status = PlayerStatus.online;
        message = 'Servidor encontrado: $found';
      });
      await controller.loadRequest(Uri.parse(playerUrl!));
    } else {
      _markOfflineAndRetry('Servidor offline. Ligue o Flask e deixe a TV Box na mesma rede do computador.');
    }
  }

  void _markOfflineAndRetry(String text) {
    if (!mounted) return;
    setState(() {
      status = PlayerStatus.offline;
      message = text;
    });
    retryTimer?.cancel();
    retryTimer = Timer(const Duration(seconds: 8), _startDiscovery);
  }

  Future<void> _healthCheckOrReconnect() async {
    final base = serverBaseUrl;
    if (base == null) {
      await _startDiscovery();
      return;
    }
    final ok = await _canOpen('$base$playerPath');
    if (!ok) {
      _markOfflineAndRetry('Servidor indisponível. Tentando encontrar novamente...');
    } else {
      SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);
    }
  }

  Future<String?> _findServer() async {
    final tested = <String>{};

    for (final host in preferredHosts) {
      tested.add(host);
      final base = 'http://$host:$serverPort';
      if (await _canOpen('$base$playerPath')) return base;
    }

    final localHosts = await _getLocalIPv4Hosts();
    final subnets = <String>{};
    for (final host in localHosts) {
      final parts = host.split('.');
      if (parts.length == 4) {
        subnets.add('${parts[0]}.${parts[1]}.${parts[2]}');
      }
    }

    // Redes mais comuns em roteadores domésticos/campus.
    subnets.addAll(['192.168.15', '192.168.0', '192.168.1', '10.0.0']);

    for (final subnet in subnets) {
      for (var start = 1; start <= 254; start += 32) {
        final futures = <Future<String?>>[];
        for (var i = start; i < start + 32 && i <= 254; i++) {
          final host = '$subnet.$i';
          if (tested.contains(host)) continue;
          tested.add(host);
          futures.add(_testHost(host));
        }
        final results = await Future.wait(futures);
        for (final base in results) {
          if (base != null) return base;
        }
      }
    }

    return null;
  }

  Future<String?> _testHost(String host) async {
    final base = 'http://$host:$serverPort';
    return await _canOpen('$base$playerPath') ? base : null;
  }

  Future<bool> _canOpen(String url) async {
    final client = HttpClient()..connectionTimeout = const Duration(milliseconds: 700);
    try {
      final request = await client.getUrl(Uri.parse(url)).timeout(const Duration(milliseconds: 900));
      final response = await request.close().timeout(const Duration(milliseconds: 1200));
      await response.drain<void>();
      return response.statusCode >= 200 && response.statusCode < 500;
    } catch (_) {
      return false;
    } finally {
      client.close(force: true);
    }
  }

  Future<List<String>> _getLocalIPv4Hosts() async {
    try {
      final interfaces = await NetworkInterface.list(
        includeLoopback: false,
        type: InternetAddressType.IPv4,
      );
      return interfaces
          .expand((i) => i.addresses)
          .map((a) => a.address)
          .where((ip) => !ip.startsWith('127.'))
          .toList();
    } catch (_) {
      return const [];
    }
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);
      _healthCheckOrReconnect();
    }
  }

  @override
  void dispose() {
    retryTimer?.cancel();
    keepAliveTimer?.cancel();
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: false,
      child: Scaffold(
        backgroundColor: Colors.black,
        body: Stack(
          children: [
            if (status == PlayerStatus.online) WebViewWidget(controller: controller),
            if (status != PlayerStatus.online) _OfflineView(status: status, message: message),
          ],
        ),
      ),
    );
  }
}

class _OfflineView extends StatelessWidget {
  const _OfflineView({required this.status, required this.message});

  final PlayerStatus status;
  final String message;

  @override
  Widget build(BuildContext context) {
    final searching = status == PlayerStatus.searching;
    return Container(
      width: double.infinity,
      height: double.infinity,
      color: Colors.black,
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.cast_connected, color: Color(0xFF2E7DFF), size: 74),
              const SizedBox(height: 22),
              const Text(
                'Conecta Campus',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.white, fontSize: 34, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 14),
              Text(
                searching ? 'Procurando servidor...' : 'Servidor offline',
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.white70, fontSize: 24, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 12),
              Text(
                message,
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.white54, fontSize: 18),
              ),
              const SizedBox(height: 28),
              const SizedBox(
                width: 42,
                height: 42,
                child: CircularProgressIndicator(strokeWidth: 4),
              ),
              const SizedBox(height: 18),
              const Text(
                'Quando o servidor voltar, o player abre automaticamente.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.white38, fontSize: 16),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
