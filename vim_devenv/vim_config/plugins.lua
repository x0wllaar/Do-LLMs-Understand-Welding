return {
    -- JSONc syntax
    {"neoclide/jsonc.vim"},

    -- LSP
    {"williamboman/mason.nvim"},
    {"williamboman/mason-lspconfig.nvim"},
    {"neovim/nvim-lspconfig"},

    -- Vscode-like pictograms
    {
            "onsails/lspkind.nvim",
            event = { "VimEnter" },
    },

    -- Auto-completion engine
    {
            "hrsh7th/nvim-cmp",
            dependencies = {
                    "lspkind.nvim",
                    "hrsh7th/cmp-nvim-lsp", -- lsp auto-completion
                    "hrsh7th/cmp-buffer", -- buffer auto-completion
                    "hrsh7th/cmp-path", -- path auto-completion
                    "hrsh7th/cmp-cmdline", -- cmdline auto-completion
            },
            config = function()
                    require("local.completions")
            end,
    },
    
    -- Code snippet engine
	{
		"L3MON4D3/LuaSnip",
		version = "v2.*",
	},

    {
          "folke/trouble.nvim",
          opts = {}, -- for default options, refer to the configuration section for custom setup.
          cmd = "Trouble",
          keys = {
            {
              "<leader>xx",
              "<cmd>Trouble diagnostics toggle<cr>",
              desc = "Diagnostics (Trouble)",
            },
            {
              "<leader>xX",
              "<cmd>Trouble diagnostics toggle filter.buf=0<cr>",
              desc = "Buffer Diagnostics (Trouble)",
            },
            {
              "<leader>cs",
              "<cmd>Trouble symbols toggle focus=false<cr>",
              desc = "Symbols (Trouble)",
            },
            {
              "<leader>cl",
              "<cmd>Trouble lsp toggle focus=false win.position=right<cr>",
              desc = "LSP Definitions / references / ... (Trouble)",
            },
            {
              "<leader>xL",
              "<cmd>Trouble loclist toggle<cr>",
              desc = "Location List (Trouble)",
            },
            {
              "<leader>xQ",
              "<cmd>Trouble qflist toggle<cr>",
              desc = "Quickfix List (Trouble)",
            },
          },
}
}
