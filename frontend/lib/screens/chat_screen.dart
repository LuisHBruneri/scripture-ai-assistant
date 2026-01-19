import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:hive_flutter/hive_flutter.dart';
import '../models/message.dart';
import '../services/api_service.dart';
import '../widgets/typing_indicator.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final ApiService _apiService = ApiService();
  final ScrollController _scrollController = ScrollController();
  final List<Message> _messages = [];
  bool _isLoading = false;
  late Box _chatBox;

  @override
  void initState() {
    super.initState();
    _loadMessages();
  }

  void _loadMessages() {
    _chatBox = Hive.box('chat_history');
    final savedMessages = _chatBox.get('messages', defaultValue: []);
    if (savedMessages != null && savedMessages is List) {
      setState(() {
        _messages.addAll(savedMessages.map((msg) {
          // Hive stores Map<dynamic, dynamic>, need to cast
          final map = Map<String, dynamic>.from(msg);
          return Message(
            text: map['text'],
            isUser: map['isUser'],
            sources: map['sources'] != null ? List<String>.from(map['sources']) : null,
          );
        }).toList());
      });
      // Scroll to bottom after loading
      Future.delayed(const Duration(milliseconds: 500), _scrollToBottom);
    }
  }

  void _saveMessages() {
    final messagesJson = _messages.map((msg) => {
      'text': msg.text,
      'isUser': msg.isUser,
      'sources': msg.sources,
    }).toList();
    _chatBox.put('messages', messagesJson);
  }

  Future<void> _clearHistory() async {
    setState(() {
      _messages.clear();
    });
    await _chatBox.delete('messages');
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _sendMessage() async {
    if (_controller.text.trim().isEmpty) return;

    final query = _controller.text;
    setState(() {
      _messages.add(Message(text: query, isUser: true));
      _isLoading = true;
    });
    _saveMessages(); // Save user message
    _controller.clear();
    _scrollToBottom();

    // Placeholder for AI or Typing Indicator logic
    // We add an empty message to start filling it
    bool hasStarted = false;

    try {
      await for (final chunk in _apiService.sendMessageStream(query)) {
        if (!hasStarted) {
           setState(() {
             _isLoading = false; // Stop generic loading, we are now streaming
             _messages.add(Message(text: "", isUser: false));
           });
           hasStarted = true;
        }

        if (chunk['type'] == 'content') {
          final textChunk = chunk['data'] as String;
          if (mounted) {
            setState(() {
              final lastMsg = _messages.last;
              _messages[_messages.length - 1] = Message(
                text: lastMsg.text + textChunk,
                isUser: false,
                sources: lastMsg.sources,
              );
            });
            _scrollToBottom();
          }
        } else if (chunk['type'] == 'sources') {
          final sources = (chunk['data'] as List).cast<String>();
          if (mounted) {
            setState(() {
              final lastMsg = _messages.last;
              _messages[_messages.length - 1] = Message(
                text: lastMsg.text,
                isUser: false,
                sources: sources,
              );
            });
            _saveMessages(); // Save after getting sources
            _scrollToBottom();
          }
        } else if (chunk['type'] == 'error') {
           final errorMsg = chunk['data'] as String;
           if (mounted) {
             setState(() {
               final lastMsg = _messages.last;
               // If message was empty, just show error. If it had content, append error.
               final newText = lastMsg.text.isEmpty 
                   ? "⚠️ Erro: $errorMsg" 
                   : lastMsg.text + "\n\n⚠️ Erro: $errorMsg";
               
               _messages[_messages.length - 1] = Message(
                 text: newText,
                 isUser: false,
                 sources: lastMsg.sources,
               );
             });
             _saveMessages(); // Save error state
             _scrollToBottom();
           }
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          // If we never started streaming, show error as a new message
          if (!hasStarted) {
             _messages.add(Message(
            text: "Erro: Não foi possível conectar ao servidor. (${e.toString()})",
            isUser: false,
          ));
          } else {
             // Append error to current message
             final lastMsg = _messages.last;
             _messages[_messages.length - 1] = Message(
                text: lastMsg.text + "\n[Erro de conexão interrompeu a resposta]",
                isUser: false,
                sources: lastMsg.sources,
             );
          }
        });
        _saveMessages(); // Save exception state
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
        _saveMessages(); // Final save to be sure
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFDFBF7), // Parchment / Old Paper
      appBar: AppBar(
        title: Text('Scriptura AI', style: GoogleFonts.cinzel(fontWeight: FontWeight.bold, fontSize: 22)),
        centerTitle: true,
        backgroundColor: const Color(0xFF800020), // Burgundy
        foregroundColor: const Color(0xFFFDFBF7), // Parchment text
        elevation: 4,
        shadowColor: Colors.black45,
        iconTheme: const IconThemeData(color: Color(0xFFFDFBF7)),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_outline),
            tooltip: 'Limpar Conversa',
            onPressed: () {
              showDialog(
                context: context,
                builder: (ctx) => AlertDialog(
                  backgroundColor: const Color(0xFFFDFBF7),
                  title: Text('Limpar Histórico?', style: GoogleFonts.cinzel(fontWeight: FontWeight.bold, color: const Color(0xFF800020))),
                  content: Text('Isso apagará todas as mensagens desta conversa.', style: GoogleFonts.crimsonText(fontSize: 18)),
                  actions: [
                    TextButton(
                      child: Text('Cancelar', style: GoogleFonts.cinzel(color: Colors.grey)),
                      onPressed: () => Navigator.of(ctx).pop(),
                    ),
                    TextButton(
                      child: Text('Limpar', style: GoogleFonts.cinzel(color: const Color(0xFF800020), fontWeight: FontWeight.bold)),
                      onPressed: () {
                        Navigator.of(ctx).pop();
                        _clearHistory();
                      },
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 20.0),
              itemCount: _messages.length + (_isLoading ? 1 : 0),
              itemBuilder: (context, index) {
                if (_isLoading && index == _messages.length) {
                  return _buildTypingIndicator(); // Show dot animation
                }
                final message = _messages[index];
                return _buildMessageBubble(message);
              },
            ),
          ),
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Align(
      alignment: Alignment.centerLeft,
      child: Padding(
        padding: const EdgeInsets.only(bottom: 12.0),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            CircleAvatar(
               backgroundColor: const Color(0xFF800020), // Burgundy
               radius: 16,
               child: const Icon(Icons.menu_book, size: 18, color: Color(0xFFFDFBF7)),
            ),
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(16),
                  topRight: Radius.circular(16),
                  bottomRight: Radius.circular(16),
                  bottomLeft: Radius.circular(4),
                ),
                boxShadow: [
                  BoxShadow(color: Colors.brown.withOpacity(0.1), blurRadius: 6, offset: const Offset(0, 3)),
                ],
                border: Border.all(color: const Color(0xFFE0D0B8), width: 0.5),
              ),
              child: const TypingIndicator(color: Color(0xFF800020)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMessageBubble(Message message) {
    final isUser = message.isUser;
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Padding(
        padding: const EdgeInsets.only(bottom: 18.0),
        child: Row(
          mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            if (!isUser) ...[
              CircleAvatar(
                 backgroundColor: const Color(0xFF800020),
                 radius: 16,
                 child: const Icon(Icons.menu_book, size: 18, color: Color(0xFFFDFBF7)),
              ),
              const SizedBox(width: 10),
            ],
            Flexible(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
                decoration: BoxDecoration(
                  color: isUser ? const Color(0xFF800020) : Colors.white,
                  borderRadius: BorderRadius.only(
                    topLeft: const Radius.circular(20),
                    topRight: const Radius.circular(20),
                    bottomLeft: Radius.circular(isUser ? 20 : 4),
                    bottomRight: Radius.circular(isUser ? 4 : 20),
                  ),
                  boxShadow: [
                     BoxShadow(color: Colors.brown.withOpacity(0.1), blurRadius: 4, offset: const Offset(0, 2)),
                  ],
                  border: isUser ? null : Border.all(color: const Color(0xFFE0D0B8), width: 0.5),
                ),
                child: SelectionArea(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      isUser
                          ? Text(
                              message.text,
                              style: GoogleFonts.crimsonText(color: const Color(0xFFFDFBF7), fontSize: 18, height: 1.3),
                            )
                          : MarkdownBody(
                              data: message.text,
                              selectable: true, 
                              styleSheet: MarkdownStyleSheet(
                                p: GoogleFonts.crimsonText(color: const Color(0xFF2D241E), fontSize: 18, height: 1.4),
                                strong: GoogleFonts.crimsonText(fontWeight: FontWeight.bold),
                                h1: GoogleFonts.cinzel(fontSize: 24, fontWeight: FontWeight.bold, color: const Color(0xFF800020)),
                                h2: GoogleFonts.cinzel(fontSize: 20, fontWeight: FontWeight.bold, color: const Color(0xFF5D4037)),
                                h3: GoogleFonts.cinzel(fontSize: 18, fontWeight: FontWeight.bold, color: const Color(0xFF5D4037)),
                                blockquote: GoogleFonts.crimsonText(fontSize: 18, fontStyle: FontStyle.italic, color: Colors.grey[700]),
                                blockquoteDecoration: BoxDecoration(
                                  color: const Color(0xFFF5F5F5),
                                  border: Border(left: BorderSide(color: const Color(0xFF800020), width: 4)),
                                  borderRadius: BorderRadius.circular(4),
                                ),
                              ),
                            ),
                      if (!isUser && message.sources != null && message.sources!.isNotEmpty)
                        Padding(
                          padding: const EdgeInsets.only(top: 10.0),
                          child: Row(
                            children: [
                              const Icon(Icons.local_library, size: 12, color: Colors.grey),
                              const SizedBox(width: 4),
                              Expanded(
                                child: Text(
                                  "Fontes: ${message.sources!.join(', ')}",
                                  style: GoogleFonts.cinzel(fontSize: 10, color: Colors.grey[700], fontWeight: FontWeight.w600),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ],
                          ),
                        ),
                      
                      // Copy Button Row
                      Padding(
                        padding: const EdgeInsets.only(top: 8.0),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.end,
                          children: [
                             InkWell(
                               onTap: () {
                                 Clipboard.setData(ClipboardData(text: message.text));
                                 ScaffoldMessenger.of(context).showSnackBar(
                                   SnackBar(
                                     content: Text('Texto copiado!', style: GoogleFonts.crimsonText(color: Colors.white)),
                                     backgroundColor: const Color(0xFF800020),
                                     duration: const Duration(seconds: 1),
                                   ),
                                 );
                               },
                               child: Padding(
                                 padding: const EdgeInsets.all(4.0),
                                 child: Icon(
                                   Icons.copy_all,
                                   size: 18,
                                   color: isUser ? Colors.white54 : Colors.brown[300],
                                 ),
                               ),
                             ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            if (isUser) ...[
              const SizedBox(width: 10),
              const CircleAvatar(
                 backgroundColor: Color(0xFF5D4037), // Dark earth/wood
                 radius: 16,
                 child: Icon(Icons.person, size: 18, color: Color(0xFFFDFBF7)),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 16.0),
      decoration: BoxDecoration(
        color: const Color(0xFFFDFBF7),
        boxShadow: [
           BoxShadow(color: Colors.brown.withOpacity(0.05), blurRadius: 4, offset: const Offset(0, -2)),
        ],
        border: const Border(top: BorderSide(color: Color(0xFFE0D0B8), width: 0.5)),
      ),
      child: SafeArea(
        child: Row(
          children: [
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: const Color(0xFFD7CCC8)), // Light brown border
                ),
                child: TextField(
                  controller: _controller,
                  decoration: InputDecoration(
                    hintText: 'Pergunte às Escrituras...',
                    hintStyle: GoogleFonts.crimsonText(color: Colors.grey[500], fontSize: 18, fontStyle: FontStyle.italic),
                    border: InputBorder.none,
                    contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                  ),
                  onSubmitted: (_) => _sendMessage(),
                  style: GoogleFonts.crimsonText(fontSize: 18, color: const Color(0xFF2D241E)),
                  cursorColor: const Color(0xFF800020),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Container(
              decoration: BoxDecoration(
                color: const Color(0xFF800020),
                shape: BoxShape.circle,
                boxShadow: [
                   BoxShadow(color: const Color(0xFF800020).withOpacity(0.4), blurRadius: 8, offset: const Offset(0, 4)),
                ],
              ),
              child: IconButton(
                icon: const Icon(Icons.send_rounded, color: Color(0xFFFDFBF7)),
                onPressed: _sendMessage,
                tooltip: 'Enviar',
              ),
            ),
          ],
        ),
      ),
    );
  }
}
